## _there is a lot of broken things here!!!! dont expect this to just work, i have no idea what im doing!_ 

this is working nnunetv2 extension for me (working as in a massive work in progress), lots of stuff likely does not work. i have also very likely missed some credits and for that i very much apologize, i am slowly working through better attributing all of these as i get them functional

many thanks to nnunet and all of the people's work i have included in here for making machine learning accesible for a person without a phd :)
# nnunetv2
from here: https://github.com/MIC-DKFZ/nnUNet

# extra network architectures
_some configs will need to be changed for <24gb vram, noted ones i have found below_

- Swin-UNETR -- reduced feature size from 48 to 24. on 200^3 volume bs2 this took 22 gb vram
- SegResNet -- default 
- MedNeXt 
- LightM-UNet -- reduced initial feature size from 32 to 8, on 200^3 this took 19gb vram
- U-Mamba at bottleck -- default
- U-Mamba encoder -- divided init feature by two, on 200^3 this took 16.5gb vram
- SAMed -- not yet tested, 2d only
- UNETR - defaults -- 200^3 took just over 9gb vram

from TriALS here: https://github.com/xmed-lab/TriALS/tree/main

other UMamba and some others from here (also another appearance from the legend junma11): https://github.com/bowang-lab/U-Mamba/tree/main

to use extra nets, specify trainer like so : 
```CUDA_VISIBLE_DEVICES=0 nnUNetv2_train 3 3d_fullres 0 -tr nnUNetTrainerUMambaBot```
# extra losses
from multiple sources -- 

some from jun ma here: https://github.com/JunMa11/SegLossOdyssey

dist from andy s ding here: https://github.com/andy-s-ding/nnUNet/tree/tbone-nnunet

nextOU topology aware losses from here: https://github.com/PengchengShi1220/NexToU?tab=readme-ov-file

some have their own trainer class, some do not, i have not finished implementing most of theese 

