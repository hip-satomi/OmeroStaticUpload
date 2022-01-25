FROM continuumio/anaconda3:2021.11

# TODO: install java
RUN apt-get clean
RUN apt-get update
RUN apt-get install -y --no-install-recommends libgl1-mesa-glx ca-certificates wget
RUN rm -rf /var/lib/apt/lists/*

ENV MAMBA_ROOT_PREFIX="/opt/conda"
ENV ENV_NAME="base"

RUN useradd -ms /bin/bash appuser 
#&& \
    #mkdir -p "$MAMBA_ROOT_PREFIX" && \
    #chmod -R a+rwx "$MAMBA_ROOT_PREFIX" "/home" && \
    #export ENV_NAME="$ENV_NAME" 

RUN chown -R appuser /opt/conda

USER appuser
WORKDIR /home/appuser

RUN conda install python=3.8 omero-py openjdk wget=1.20.1 p7zip -c bioconda -c ome -c conda-forge \
 && conda clean -afy

ENV OMERO_URL="omero"
ENV OMERO_PORT="4064"
ENV OMERO_USERNAME="root"
ENV OMERO_PASSWORD="omero"

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

#COPY ./data ./data

COPY ./download_data.sh ./

COPY ./run_cellsium.sh ./

#RUN bash ./download_data.sh
RUN bash ./run_cellsium.sh

COPY ./main.py ./

CMD ["python", "main.py"]
