path="/data/Simulation_Project/Simulation_Dataset/"

mkdir -p ${path}

python -m cellsium -t SimulationDuration=8 --Output TiffOutput -o ${path}/sim1 -t Seed=1
python -m cellsium -t SimulationDuration=8 --Output TiffOutput -o ${path}/sim2 -t Seed=2
python -m cellsium -t SimulationDuration=8 --Output TiffOutput -o ${path}/sim3 -t Seed=3
python -m cellsium -t SimulationDuration=8 --Output TiffOutput -o ${path}/sim4 -t Seed=4
python -m cellsium -t SimulationDuration=8 --Output TiffOutput -o ${path}/sim5 -t Seed=5
