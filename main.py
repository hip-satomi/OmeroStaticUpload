# TODO: iterate data folder
# -- upload tif files to omero
# -- add rois when available

import os
import os.path as osp
import glob
import subprocess
import acia
import logging
from acia.segm.omero.utils import list_projects, list_datasets_in_project, list_images_in_dataset, create_dataset, create_project
from acia.segm.local import ImageJRoISource
from acia.segm.omero.storer import OmeroRoIStorer
import omero
from omero.gateway import BlitzGateway
from omero.gateway import ProjectWrapper, DatasetWrapper

omero_url = os.environ.get('OMERO_URL', 'ibt056')
omero_port = int(os.environ.get('OMERO_PORT', 4064))
username = os.environ.get('OMERO_USERNAME', 'root')
password = os.environ.get('OMERO_PASSWORD', 'omero')

credentials = dict(
    serverUrl=omero_url,
    username=username,
    password=password,
    port=omero_port
)

base_path = 'data'

# open omero connection
with BlitzGateway(username, password, host=omero_url, port=omero_port, secure=True) as conn:
    for project_name in os.listdir(base_path):
        # check if project exists
        projects = list_projects(conn)
        projects = list(filter(lambda p: p.getName() == project_name, projects))

        if len(projects) > 1:
            logging.error(f'Project name "{project_name}" exists multiple times in omero setup! Skip due to ambiguity!')
            continue

        project = None

        if len(projects) == 0:
            project = create_project(conn, project_name=project_name)
            logging.info(f'Create Project "{project_name}"')
        
        if len(projects) == 1:
            project = projects[0]
            logging.info(f'Project "{project_name}" already exists')


        for dataset_name in os.listdir(osp.join(base_path, project_name)):
            # check if dataset exists
            datasets = list_datasets_in_project(conn, project.getId())
            datasets = list(filter(lambda d: d.getName() == dataset_name, datasets))

            if len(datasets) > 1:
                logging.error(f'Dataset name "{dataset_name}" exists multiple times in omero setup! Skip due to ambiguity!')
                continue

            dataset = None

            if len(datasets) == 0:
                dataset = create_dataset(conn, projectId = project.getId(), dataset_name=dataset_name)
                logging.info(f'Create Project "{project_name}"')
            
            if len(datasets) == 1:
                dataset = datasets[0]
                logging.info(f'Project "{dataset_name}" already exists')

            for file_path in glob.glob(os.path.join(base_path, project_name, dataset_name, '*.tif')):
                # check if file already exists
                file_name = osp.basename(file_path)
                files = list_images_in_dataset(conn, dataset.getId())
                files = list(filter(lambda f: f.getName() == file_name, files))

                omero_path = f'{project_name}/{dataset_name}/{file_name}'
                if len(files) > 1:
                    logging.info(f'Image with name "{omero_path}" already exists in omero')
                else:
                    # upload file
                    print('Upload')
                    subprocess.run(f'omero import -s {omero_url} -u {username} -w {password} -d {dataset.getId()} {file_path} ', shell=True)
                    print(f'Create {omero_path}')

                    files = list_images_in_dataset(conn, dataset.getId())
                    files = list(filter(lambda f: f.getName() == file_name, files))
                    image = files[0]

                    # TODO: upload RoIs
                            # create roi source
                    ijrs = ImageJRoISource(file_path)
                    # lookup omero image id
                    image_id = image.getId()

                    # upload RoIs
                    print(f"Filename: {file_path}, imageId: {image_id}, overlay size: {len(ijrs.overlay.contours)}")
                    if len(ijrs.overlay) > 0:
                        OmeroRoIStorer.store(ijrs.overlay, image_id, **credentials)