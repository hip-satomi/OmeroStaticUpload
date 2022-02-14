FROM continuumio/anaconda3:2021.11

# Make RUN commands use `bash --login`:
SHELL ["/bin/bash", "--login", "-c"]

# TODO: install java
RUN apt-get clean && \
    apt-get update && \
    apt-get install -y --no-install-recommends libgl1-mesa-glx ca-certificates wget openjdk-17-jre && \
    rm -rf /var/lib/apt/lists/*

RUN conda create -n cellsium python=3.8 cellsium -c modsim -c conda-forge \
 && conda clean -afy

# Initialize conda in bash config fiiles:
RUN conda init bash

# Activate the environment, and make sure it's activated:
RUN echo "conda activate cellsium" > ~/.bashrc

COPY ./run_cellsium.sh ./
RUN bash ./run_cellsium.sh

FROM continuumio/anaconda3:2021.11

# Make RUN commands use `bash --login`:
SHELL ["/bin/bash", "--login", "-c"]

# TODO: install java
RUN apt-get clean && \
    apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates openjdk-17-jre && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash appuser
RUN chmod a+rwx /opt/conda/

USER appuser
WORKDIR /home/appuser

# copy data from previous stage
COPY --from=0 /data/ ./data/

# Initialize conda in bash config fiiles:
RUN conda init bash

# create conda environment with omero-py installed
RUN conda create -n omero omero-py -c ome \
 && conda clean -afy

# Activate the environment, and make sure it's activated:
RUN echo "conda activate omero" > ~/.bashrc

ENV OMERO_URL="omero"
ENV OMERO_PORT="4064"
ENV OMERO_USERNAME="root"
ENV OMERO_PASSWORD="omero"

COPY ./main.py ./
COPY ./utils.py ./

CMD ["conda", "run", "-n", "omero", "python", "main.py"]
