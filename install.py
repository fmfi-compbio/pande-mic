import os

print("This is an interactive script to install pande-mic. In case that anything fails, please refer to the repository README or open an issue on gitHub. Also, we assume, taht you have cloned the pande-mic repository from github and you are runnning this script from there.")
print("------------------------------------ conda -----------------------------------------------------")
print("We use conda to install and manage packages needed for pande-mic. It is possible you already have it installed, so we will check this first:")
print("if the next command fails (i.e. output is something like 'conda: command not found'), please install conda):")
print("RUNNING: conda --version")
os.system("conda --version")
install_conda = input("install conda (64bit linux version)?[y/n]")
if install_conda == 'y':
    print("RUNNING: wget https://repo.anaconda.com/miniconda/Miniconda3-py310_23.1.0-1-Linux-x86_64.sh && chmod +x ./Miniconda3-py310_23.1.0-1-Linux-x86_64.sh && ./Miniconda3-py310_23.1.0-1-Linux-x86_64.sh")
    os.system("wget https://repo.anaconda.com/miniconda/Miniconda3-py310_23.1.0-1-Linux-x86_64.sh && chmod +x ./Miniconda3-py310_23.1.0-1-Linux-x86_64.sh && ./Miniconda3-py310_23.1.0-1-Linux-x86_64.sh")
    print("----- conda config ----- ")
    print("running bash inictialization script to make new installation available in the current shell - you will probably need to re-run the script, skipping the conda install steps")
    print("RUNNING:. ~/.bashrc")
    os.system(". ~/.bashrc")
    #print("RUNNING: exec bash")
    #os.system("exec bash")
else:
    print("assuming that conda is already installed on the sytem, skipping conda install")

print ("------------------------------ end of conda install --------------------------------------------")

print("-------------- conda config and test - after installation --------------")
autoactivate = input("initialize conda not to auto-activate base environment? [y/n]")
if autoactivate == 'y':
    print("RUNNING: conda config --set auto_activate_base false")
    os.system("conda config --set auto_activate_base false")
print("---- test conda ----")
print("the conda version check should now print something like 'conda 23.1.0' ")
print("RUNNING: conda --version")
os.system("conda --version")
print("-------------- end of conda config and test -------------------")



print("--------------------------- conda environment -------------------------------")
print("Now we will create the conda environment. Please proceed only if the conda install step was sucessfull or conda was already installed on the system")
conda_success = input("proceed?[y/n]")
if conda_success == 'n':
    exit(1)
elif conda_success == 'y':
    print("some libraries require gcc in the installation process, so we have to chcek it is installled - again, it should print the vesrion, not something like 'gcc: command not found':")
    print("RUNNING: gcc --version , check the output whether it is already installed on your system")
    os.system("gcc --version")
    gcc_install = input("install gcc? [y/n]")
    if gcc_install == 'y':
        print("installing gcc, root password may be required")
        print("RUNNING: sudo apt install gcc")
        os.system("sudo apt install gcc")
        print("checking gcc install, RUNNING: gcc --version")
        os.system("gcc --version")
        gcc_success = input("proceed (conda environment will be created)? [y/n]")
        if gcc_success == 'n':
            exit(1)
    else:
        print("assuming gcc is already installed on the system")
    print("creating conda environment")
    print("RUNNING: conda env create -f env.yaml")
    os.system("conda env create -f env.yaml")
    print("initializning shell for use with conda")
    print("RUNNING: conda init -all")
    os.system("conda init --all")
    #print("RUNNING:. ~/.bashrc ")
    #os.system(". ~/.bashrc")
    #print("RUNNING . ~/.bashrc.conda")
    #os.system(". ~/.bashrc.conda")
    #print("check taht environment was sucessfully created - output of next command should contain monitoring-env:")
    #print("RUNNING: conda env list")
    #os.system("conda env list")
    #print("activating the environment.. ")
    #os.system("conda activate monitoring-env")
    #os.system("source activate monitoring-env")
    #print("check that enivronment is activated - list packages in the environment - it should print a long list, starting with 'packages in environment .... miniconda3/envs/monitoring_env:':")
    #print("RINNING: conda list")
    #os.system("conda list")
    #print("check that the monitoring environment (monitoring-env) is activated - 'active environment' should be monitoring-env, NOT base")
    #print("RUNNING: conda info | grep active")
    #os.system("conda info | grep active")
    #print("if the above commands FAILED (the active environment is still base), please run the following command MANUALLY: \n conda init --all \n, then close your current shell, reopen it and run the install script again")
print("------------------------ end of conda environment setup ---------------------")

#print("please run the following command MANUALLY: \n \t conda init --all \n ")
print("Please CLOSE AND REOPEN the current shell and run \n \t conda activate monitoring_env")
#print("you may also want to run \n \t python3 env_check.py \n to make sure the environment is set up properly")

