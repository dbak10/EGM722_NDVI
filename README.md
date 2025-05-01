# EGM722_NDVI
Coursework for EGM722

This repository contains a python tool to query sentinel 2 satellite imagery from the Copernicus Data Space Ecosystem. It computes the normalised Difference Vegetation Index for a 1km2 and outputs a visualisation and useable georeferenced file for further analysis.

---

## Setup

It is necessary to have git, Conda and a working Python environment set up on your machine. All of the dependencies except one can be installed through Conda. The CDSETool will need to be installed using. 

It is recommended that the repository is forked to your own account before cloning.
The repository includes a list of the necessary dependencies as well as an ignore list to assist in correct setup. An environment.yml is included for setting up the environment correctly in Conda.

---

### CDSE tool
It is necessary to have an account registered with the CDSE via https://dataspace.copernicus.eu// It is important to have your account credentials stored in a .netrc file in your home directory. This file can only include your cdse login credentials and should be stored securely. They should be stored in the following format
machine https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token
login <your_username>
password <your_password>
This ensures that the code for the CDSEtool can authenticate your user account details and successfully query the sentinel 2 imagery. 
