## Setup the environment

*** For this part, I am using Anaconda ***
1. Install `Anaconda` on your machine. You can follow the instructions in this [guide](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html). Direct download [here](https://www.anaconda.com/products/distribution).

2. Open Anaconda Navigator and navigate to the "Environments" tab in the left panel.

3. Click on the "Import" button and select the matsimConverterEnv.yaml file located in the ./resources/setup/ folder of the cloned repository.

4. Give a name to your new environment and wait for the setup process to complete.

5. Once the environment is created, **select it** and launch an IDE like VS Code from Anaconda Navigator.

6. Open a terminal in the IDE and run the command `pip install ./resources/setup/matsim_tools-1.0.5-py3-none-any.whl` to install the required matsim_tools package. **Please verify that you are installing the lastest version available in ./resources/setup/**