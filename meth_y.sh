#!/bin/bash
#SBATCH --time=96:00:00
#SBATCH --job-name=test
#SBATCH --partition=defq
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --mem=256g
 

FLUENTNODEFILE=$(mktemp)
scontrol show hostnames > $FLUENTNODEFILE
echo "Running on nodes:"
cat $FLUENTNODEFILE
echo "### Starting at: $(date) ###"
module load ansys-uon/2024R1
module load openmpi-uoneasy/4.1.6-GCC-13.2.0
module load python-uoneasy/3.11.5-GCCcore-13.2.0
 
# Define Fluent environment
export AWP_ROOT241='{}/software/ansys_inc/v241'
 
python -m venv ansys
source ansys/bin/activate
pip install ansys.fluent.core
pip install opencv-python
 
source ansys/bin/activate
python FCS_MRF_HPC.py > log 2>&1
 
echo "### Ending at: $(date) ###"
