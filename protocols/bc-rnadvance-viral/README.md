# Beckman Coulter RNAdvance Viral RNA Isolation

### Author
[Opentrons](https://opentrons.com/)

## Categories
* Nucleic Acid Extraction & Purification
    * Beckman Coulter RNAdvance Viral

## Description
This protocol performs viral RNA isolation on up to 96 samples using the [Beckman Coulter RNAdvance Viral RNA Isolation](https://www.beckman.com/reagents/genomic/rna-isolation/viral/c63510) kit and workflow.

The protocol begins at the stage of adding binding beads to lysed samples loaded on the magnetic module in a NEST 96-deepwell plate. For reagent layout in the 2 12-channel reservoirs used in this protocol, please see "Setup" below.

For sample traceability and consistency, samples are mapped directly from the magnetic extraction plate (magnetic module, slot 6) to the elution PCR plate (temperature module, slot 1). Magnetic extraction plate well A1 is transferred to elution PCR plate A1, extraction plate well B1 to elution plate B1, ..., D2 to D2, etc.

---

![Materials Needed](https://s3.amazonaws.com/opentrons-protocol-library-website/custom-README-images/001-General+Headings/materials.png)  

To purchase tips, reagents, or pipettes, please visit our [online store](https://shop.opentrons.com/) or contact our sales team at [info@opentrons.com](mailto:info@opentrons.com)

* [Opentrons Magnetic Module (GEN2](https://shop.opentrons.com/collections/hardware-modules/products/magdeck)
* [Opentrons Temperature Module (GEN2)](https://shop.opentrons.com/collections/hardware-modules/products/tempdeck)
* [Opentrons P300 8-Channel Electronic Pipette (GEN2)](https://shop.opentrons.com/collections/ot-2-pipettes/products/8-channel-electronic-pipette)
* [Beckman Coulter RNAdvance Viral kit](https://www.beckman.com/reagents/genomic/rna-isolation/viral/c63510)
* [NEST 12 Well Reservoir 15 mL, 2x](https://labware.opentrons.com/nest_12_reservoir_15ml)
* [NEST 1 Well Reservoir 195 mL](https://labware.opentrons.com/nest_1_reservoir_195ml)
* [NEST 96 Well Plate 100 µL PCR Full Skirt](https://labware.opentrons.com/nest_96_wellplate_100ul_pcr_full_skirt)
* [NEST 96 Deepwell Plate 2mL](https://labware.opentrons.com/nest_96_wellplate_2ml_deep)
* [Opentrons 96 Filter Tip Rack 200 µL, up to 10x depending on throughput](https://shop.opentrons.com/collections/opentrons-tips/products/opentrons-200ul-filter-tips)

---
![Setup](https://s3.amazonaws.com/opentrons-protocol-library-website/custom-README-images/001-General+Headings/Setup.png)

* Entire deck
![deck](https://opentrons-protocol-library-website.s3.amazonaws.com/custom-README-images/bc-rnadvance-viral/Screen+Shot+2021-02-23+at+2.47.23+PM.png)

* Reservoir 1: slot 2
* Reservoir 2: slot 3  
![reservoirs](https://opentrons-protocol-library-website.s3.amazonaws.com/custom-README-images/bc-rnadvance-viral/Screen+Shot+2021-02-10+at+3.48.53+PM.png)

Volumes per reservoir channel: (for 96-sample run, not including dead volume):
* 10mL of 100% Isopropanol + 250uL of bead BBD
* 10mL of Wash WBE
* 10mL of 70% Ethanol
* 4mL of nuclease-free water

### Robot
* [OT-2](https://opentrons.com/ot-2)

## Process
1. Select your protocol parameters.
2. Download your protocol.
3. Upload your protocol into the [OT App](https://opentrons.com/ot-app).
4. Set up your deck according to the deck map.
5. Calibrate your labware, tiprack and pipette using the OT App. For calibration tips, check out our [support article](https://support.opentrons.com/ot-2/getting-started-software-setup/deck-calibration).
6. Hit "Run".

### Additional Notes
If you have any questions about this protocol, please contact the Protocol Development Team by filling out the [Troubleshooting Survey](https://protocol-troubleshooting.paperform.co/).

###### Internal
bc-rnadvance-viral
