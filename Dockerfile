FROM continuumio/anaconda3:2021.05

# TODO: install java

ENV MAMBA_ROOT_PREFIX="/opt/conda"
ENV ENV_NAME="base"

RUN useradd -ms /bin/bash appuser && \
    mkdir -p "$MAMBA_ROOT_PREFIX" && \
    chmod -R a+rwx "$MAMBA_ROOT_PREFIX" "/home" && \
    export ENV_NAME="$ENV_NAME" 

USER appuser

RUN conda install omero-py openjdk -c ome -c conda-forge \
 && conda clean -afy

ENV OMERO_URL="ibt056"
ENV OMERO_PORT="4064"
ENV OMERO_USERNAME="root"
ENV OMERO_PASSWORD="omero"

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY ./data ./data

COPY ./main.py ./

CMD ["python", "main.py"]