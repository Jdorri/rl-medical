# **A**natomical **L**andmark **D**etection and **D**emonstration **I**nterface <img src="examples/LandmarkDetection/DQN/images/aladdin.png" width="100" />

*ALADDIN* is a platform offering automated solutions for the detection of human anatomical landmarks using Reinforcement Learning (RL) complete with a unified visualisation suite. *ALADDIN* is a tool that can be used by medical professional within image analysis or for a wide range of tasks by machine learning researchers.  

*<p style='color:#003E74'>Please visit main directory (examples/LandmarkDetection/DQN) after installation and follow Run Instruction to run ALADDIN.</p>*

**Main Directory**: [Landmark detection using different DQN variants](examples/LandmarkDetection/DQN)

## Installation

### Dependencies
+ Python=3.8
+ [cycler=0.10.0](https://pypi.org/project/Cycler/)
+ [tensorflow-gpu=1.14.0](https://pypi.org/project/tensorflow-gpu/)
+ [tensorpack=0.9.5](https://github.com/tensorpack/tensorpack)
+ [opencv-python](https://pypi.org/project/opencv-python/)
+ [pillow](https://pypi.org/project/Pillow/)
+ [gym](https://pypi.org/project/gym/)
+ [SimpleITK](https://pypi.org/project/SimpleITK/)
+ [PyQt5](https://pypi.org/project/PyQt5/)
+ [ipython](https://pypi.org/project/ipython/)
+ [matplotlib](https://pypi.org/project/matplotlib/)

### Installation Procedure
Follow the following steps (in order) to install required dependencies.
1. ``` pip install -r requirements.txt ```
2. ``` pip install -U git+https://github.com/amiralansary/rl-medical.git ```


### Legacy Code
This project is forked from our supervisor legacy repository available on the following link:
```
https://github.com/amiralansary/rl-medical.git
```

## Authors
- **Alexander Gaskell**: aeg19@imperial.ac.uk
- **Maleakhi A. Wijaya**: maw219@imperial.ac.uk
- **Faidon Mitzalis**: fm1710@imperial.ac.uk
- **Olle Nilsson**: oen19@imperial.ac.uk
- **Harry Coppock**:
hgc19@imperial.ac.uk
- **James Dorricott**: jd3114@imperial.ac.uk

## Citation

If you use this code in your research, please cite these paper:

```
@article{alansary2019evaluating,
  title={{Evaluating Reinforcement Learning Agents for Anatomical Landmark Detection}},
  author={Alansary, Amir and Oktay, Ozan and Li, Yuanwei and Le Folgoc, Loic and 
          Hou, Benjamin and Vaillant, Ghislain and Kamnitsas, Konstantinos and 
          Vlontzos, Athanasios and Glocker, Ben and Kainz, Bernhard and Rueckert, Daniel},
  journal={Medical Image Analysis},
  year={2019},
  publisher={Elsevier}
}

@inproceedings{alansary2018automatic,
  title={Automatic view planning with multi-scale deep reinforcement learning agents},
  author={Alansary, Amir and Le Folgoc, Loic and Vaillant, Ghislain and Oktay, Ozan and Li, Yuanwei and 
  Bai, Wenjia and Passerat-Palmbach, Jonathan and Guerrero, Ricardo and Kamnitsas, Konstantinos and Hou, Benjamin and others},
  booktitle={International Conference on Medical Image Computing and Computer-Assisted Intervention},
  pages={277--285},
  year={2018},
  organization={Springer}
}
 ```
