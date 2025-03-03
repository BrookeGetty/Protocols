import math

metadata = {
    'protocolName': 'DNA extraction',
    'author': 'Steve <protocols@opentrons.com>',
    'source': 'Custom Protocol Request',
    'apiLevel': '2.9'
}


def run(ctx):

    ctx.set_rail_lights(True)

    [dry_time, increment_vol, baseline_vol, choose_tip_rack,
     uploaded_csv] = get_values(  # noqa: F821
        "dry_time", "increment_vol", "baseline_vol", "choose_tip_rack",
        "uploaded_csv")

    # sample volume from manifest
    ml_line = uploaded_csv.splitlines()[3]
    sample_volume = int(float(ml_line[
     ml_line.find(',')+1:ml_line.find(' ml')])*1000)

    # tips (max volume 200 ul if filter tips, otherwise 300 ul)
    tips_300 = [ctx.load_labware(choose_tip_rack, slot) for slot in ['6', '9']]
    tip_max = tips_300[0].wells_by_name()['A1'].max_volume

    # p300 multi
    p300m = ctx.load_instrument(
        "p300_multi", 'right', tip_racks=tips_300)

    # primary DNA extraction plate in slot 2
    dna_extraction_plates = [ctx.load_labware(
     "usascientific_96_wellplate_2.4ml_deep", '2')]

    # slot 1 first for sample plate, later for water
    sample_plate = deep_well = ctx.load_labware(
     "usascientific_96_wellplate_2.4ml_deep", '1')

    # slot 3 first for premix, then wash, then ethanol
    reagent_reservoir = ctx.load_labware("nest_1_reservoir_195ml", '3')
    premix = wash = etoh = reagent_reservoir.wells()[0].bottom(3)

    # waste reservoir
    reservoir = ctx.load_labware("nest_1_reservoir_195ml", '11')
    waste = reservoir.wells()[0]

    # pcr plate for eluate in slot 10
    elution_plate = ctx.load_labware(
     "nest_96_wellplate_100ul_pcr_full_skirt", '10')

    # volume of sample and premix to be dispensed to primary extraction plate
    vol_increments = math.floor((sample_volume - baseline_vol) / increment_vol)
    if vol_increments > 4:
        vol_increments = 4
    vol_primary = baseline_vol + ((vol_increments in [1, 3, 4])*increment_vol)
    if vol_primary == 500:
        premix_vol = 633
    else:
        premix_vol = 950

    # duplicate extraction plate in slot 5 if sample volume >= 1.0 mL
    dna_extraction_plate = dna_extraction_plates[0]
    if sample_volume >= 1000:
        dna_extraction_plates.append(ctx.load_labware(
         "usascientific_96_wellplate_2.4ml_deep", '5'))
        duplicate_extraction_plate = dna_extraction_plates[1]
        vol_duplicate = baseline_vol + ((vol_increments in [4])*increment_vol)
        if vol_duplicate == 500:
            duplicate_premix_vol = 633
        else:
            duplicate_premix_vol = 950

    # helper function for repeat large vol transfers
    def rep_max_transfer(remaining, source, dest, tip_max_vol=tip_max, air=0):
        vol = tip_max_vol - air
        while remaining > vol:
            p300m.aspirate(vol, source)
            if air > 0:
                p300m.air_gap(air)
            p300m.dispense(tip_max_vol, dest)
            remaining -= vol
        p300m.aspirate(remaining, source)
        if air > 0:
            p300m.air_gap(air)
        p300m.dispense(remaining + air, dest)

    # mix premix and distribute to DNA extraction plates
    p300m.pick_up_tip()
    for index, plate in enumerate(dna_extraction_plates):
        for column in plate.columns():
            p300m.mix(5, tip_max, premix)
            if index == 0:
                rep_max_transfer(premix_vol, premix, column[0])
            else:
                rep_max_transfer(duplicate_premix_vol, premix, column[0])
    p300m.drop_tip()

    # sample to DNA extraction plates
    for index, column in enumerate(sample_plate.columns()):
        p300m.pick_up_tip()
        rep_max_transfer(
         vol_primary, column[0], dna_extraction_plate.columns()[index][0])
        if sample_volume >= 1000:
            rep_max_transfer(
             vol_duplicate, column[0],
             duplicate_extraction_plate.columns()[index][0])
            p300m.mix(
             5, tip_max, duplicate_extraction_plate.columns()[index][0])
            p300m.mix(5, tip_max, dna_extraction_plate.columns()[index][0])
            p300m.drop_tip()
        else:
            p300m.mix(5, tip_max, dna_extraction_plate.columns()[index][0])
            p300m.drop_tip()

    # magnetic module with magnets disengaged
    mag = ctx.load_module('magnetic module', '4')
    mag.disengage()
    mag_plate = mag.load_labware('usascientific_96_wellplate_2.4ml_deep')
    mag_height = {
        'omni_96_wellplate_2000ul': 8.5,
        'nest_96_wellplate_2ml_deep': 8.5,
        'usascientific_96_wellplate_2.4ml_deep': 8.5
        }

    # manual steps
    ctx.set_rail_lights(False)
    ctx.pause("""Paused for the following manual steps:

                 1. Seal the plates.
                    Invert the plates 10 times to mix sample and premix.
                    Shake plates vigorously for 10 minutes on plate shaker.
                    Spin the plates.

                 2. Unseal the primary dna extraction plate and place it on
                    the OT-2 magnetic module (Slot 4). If there is a duplicate
                    plate, unseal and place it back in its original deck slot.

                 3. Remove the empty premix reservoir from the OT-2 deck
                    (Slot 3). Replace it with HKG DNA Wash Buffer 1 reservoir.

                 4. Remove the sample plate from the OT-2 deck (Slot 1).
                    Replace it with a deep well plate containing water
                    (in column 1) for the elution step.

                 5. Refill the tip boxes in slots 6 and 9.

                 6. Click resume in the OT app.""")

    ctx.set_rail_lights(True)
    p300m.reset_tipracks()

    # helper function to remove waste from mag plate
    def remove_waste(waste_vol):
        for index, column in enumerate(mag_plate.columns()):
            p300m.pick_up_tip()
            rep_max_transfer(waste_vol, column[0], waste)
            p300m.drop_tip()

    # helper function to transfer reagent from origin to target plate
    def add_reagent(origin, target, add_vol):
        for index, column in enumerate(target.columns()):
            rep_max_transfer(add_vol, origin, column[0].top())

    # engage magnets 20 min (primary DNA extraction plate)
    mag.engage(height=mag_height['usascientific_96_wellplate_2.4ml_deep'])
    ctx.delay(minutes=20)

    # remove sup, final traces of sup (primary DNA extraction plate)
    remove_waste(premix_vol + vol_primary)
    remove_waste(50)

    if sample_volume >= 1000:
        ctx.set_rail_lights(False)
        ctx.pause("""Please remove the primary plate from the magnetic module
                     and return it to its previous deck slot.
                     Please place the duplicate DNA extraction plate on the
                     magnetic module. Please replenish the tip boxes in slots 6
                     and 9.""")
        ctx.set_rail_lights(True)
        p300m.reset_tipracks()

        # engage magnets 20 min (duplicate dna extraction plate)
        mag.disengage()
        mag.engage(height=mag_height['usascientific_96_wellplate_2.4ml_deep'])
        ctx.delay(minutes=20)

        # add 400 ul HKG DNA Wash Buffer 1 to primary dna extraction plate
        p300m.pick_up_tip()
        add_reagent(wash, dna_extraction_plate, 400)
        p300m.drop_tip()

        ctx.set_rail_lights(False)
        ctx.pause("""Please replenish the tip boxes in slots 6
                     and 9.""")
        ctx.set_rail_lights(True)
        p300m.reset_tipracks()

        # remove sup, remaining traces of sup (duplicate DNA extraction plate)
        remove_waste(duplicate_premix_vol + vol_duplicate)
        remove_waste(50)

        ctx.set_rail_lights(False)
        ctx.pause("""Please replenish the tip boxes in slots 6
                     and 9.""")
        ctx.set_rail_lights(True)
        p300m.reset_tipracks()

        # suspend primary plate beads, move to duplicate wells to combine
        for index, column in enumerate(dna_extraction_plate.columns()):
            p300m.pick_up_tip()
            p300m.mix(5, tip_max, column[0])
            rep_max_transfer(400, column[0], mag_plate.columns()[index][0])
            p300m.drop_tip()

        # suspend with additional 100 ul HKG DNA Wash Buffer 1, combine
        p300m.pick_up_tip()
        add_reagent(wash, dna_extraction_plate, 100)
        p300m.drop_tip()

        ctx.set_rail_lights(False)
        ctx.pause("""Please replenish the tip boxes in slots 6
                     and 9.""")
        ctx.set_rail_lights(True)
        p300m.reset_tipracks()

        for index, column in enumerate(dna_extraction_plate.columns()):
            p300m.pick_up_tip()
            p300m.mix(5, 100, column[0])
            p300m.aspirate(100, column[0])
            p300m.dispense(100, mag_plate.columns()[index][0])
            p300m.drop_tip()

    else:
        ctx.set_rail_lights(False)
        ctx.pause("""Please replenish the tip boxes in slots 6
                     and 9.""")
        ctx.set_rail_lights(True)
        p300m.reset_tipracks()

        # add 400 ul wash to primary DNA extraction plate (on magnetic module)
        p300m.pick_up_tip()
        add_reagent(wash, mag_plate, 400)
        p300m.drop_tip()

    # suspend all beads in wash on magnetic module
    for index, column in enumerate(mag_plate.columns()):
        p300m.pick_up_tip()
        p300m.mix(5, tip_max, column[0])
        p300m.drop_tip()

    mag.engage(height=mag_height['usascientific_96_wellplate_2.4ml_deep'])
    ctx.delay(minutes=7)

    ctx.set_rail_lights(False)
    ctx.pause("""Please replenish the tip boxes in slots 6
                 and 9.""")
    ctx.set_rail_lights(True)
    p300m.reset_tipracks()

    # remove sup
    if sample_volume >= 1000:
        remove_waste(500)
    else:
        remove_waste(400)

    # add 2nd wash 400 ul all beads
    p300m.pick_up_tip()
    add_reagent(wash, mag_plate, 400)
    p300m.drop_tip()

    mag.disengage()

    ctx.set_rail_lights(False)
    ctx.pause("""Please replenish the tip boxes in slots 6
                 and 9.""")
    ctx.set_rail_lights(True)
    p300m.reset_tipracks()

    # mix 2nd wash with beads
    for index, column in enumerate(mag_plate.columns()):
        p300m.pick_up_tip()
        p300m.mix(5, tip_max, column[0])
        p300m.drop_tip()

    mag.engage(height=mag_height['usascientific_96_wellplate_2.4ml_deep'])
    ctx.delay(minutes=7)

    # remove sup 2nd wash
    remove_waste(400)

    mag.disengage()

    # wash twice with 80 percent ethanol
    ctx.set_rail_lights(False)
    ctx.pause("""Please remove the wash buffer reservoir from the OT-2 deck
                 (Slot 3) and replace it with the 80 percent ethanol reservoir.
                 Please replenish the tip boxes in slots 6 and 9.""")
    ctx.set_rail_lights(True)
    p300m.reset_tipracks()

    p300m.default_speed = 200
    p300m.flow_rate.aspirate = 75
    p300m.flow_rate.dispense = 50
    for rep in range(2):
        # add 80% etoh
        p300m.pick_up_tip()
        for index, column in enumerate(mag_plate.columns()):
            rep_max_transfer(500, etoh, column[0].top(), air=50)
        p300m.drop_tip()

        # mix
        for index, column in enumerate(mag_plate.columns()):
            p300m.pick_up_tip()
            p300m.mix(5, tip_max, column[0])
            p300m.drop_tip()

        mag.engage(height=mag_height['usascientific_96_wellplate_2.4ml_deep'])
        ctx.delay(minutes=7)

        ctx.set_rail_lights(False)
        ctx.pause("""Please replenish the tip boxes in slots 6
                 and 9.""")
        ctx.set_rail_lights(True)
        p300m.reset_tipracks()

        # remove sup
        for index, column in enumerate(mag_plate.columns()):
            p300m.pick_up_tip()
            rep_max_transfer(500, column[0], waste, air=50)
            p300m.drop_tip()

        ctx.set_rail_lights(False)
        ctx.pause("""Please replenish the tip boxes in slots 6
                 and 9.""")
        ctx.set_rail_lights(True)
        p300m.reset_tipracks()

    # remove remaining traces of sup
    for index, column in enumerate(mag_plate.columns()):
        p300m.pick_up_tip()
        p300m.aspirate(50, column[0])
        p300m.air_gap(15)
        p300m.dispense(65, waste)
        p300m.drop_tip()

    p300m.default_speeed = 400
    p300m.flow_rate.aspirate = 94
    p300m.flow_rate.dispense = 94

    ctx.set_rail_lights(False)
    ctx.pause("""Please replenish the tip boxes in slots 6
                 and 9.""")
    ctx.set_rail_lights(True)
    p300m.reset_tipracks()

    # air dry
    mag.disengage()
    ctx.delay(minutes=dry_time)

    # elution: add water and mix
    water = deep_well.columns_by_name()['1'][0]
    p300m.distribute(
     23, water, mag_plate.columns(), mix_after=(3, 15), new_tip='always')

    mag.engage(height=mag_height['usascientific_96_wellplate_2.4ml_deep'])
    ctx.delay(minutes=7)

    # recover eluate to pcr plate
    p300m.transfer(
     23, mag_plate.columns(), elution_plate.columns(), new_tip='always')
    mag.disengage()

    ctx.set_rail_lights(False)
    ctx.pause("""Please remove the dna extraction plate from the magnetic
                 module. If an additional step of bead removal is needed,
                 please place the elution plate on the magnetic module, a fresh
                 pcr plate on deck slot 10, and a fresh box of tips on deck
                 slot 6.""")
    ctx.set_rail_lights(True)
    p300m.reset_tipracks()

    mag.engage()
    ctx.delay(minutes=5)

    p300m.transfer(
     23, mag_plate.columns(), elution_plate.columns(), new_tip='always')
