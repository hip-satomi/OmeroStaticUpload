import os
import os.path as osp
import glob
import subprocess
import logging
from utils import list_projects, list_datasets_in_project, list_images_in_dataset, create_dataset, create_project
from omero.gateway import BlitzGateway
import time

logging.basicConfig(level=logging.INFO)

MAX_RETRIES = 10

omero_url = os.environ.get('OMERO_URL', 'omero')
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

# testing connection
for i in range(MAX_RETRIES):
    try:
        with BlitzGateway(username, password, host=omero_url, port=omero_port, secure=True) as conn:
            # successfully established connection
            break
    except:
        # connection failed
        logging.warning(f'Cannot establish connection to omero. Try: {i}/{MAX_RETRIES}')
        # wait for 10 seconds until next try
        time.sleep(10)

        if i == MAX_RETRIES - 1:
            # never established a connection
            logging.error('All connections to omero failed!')
            exit(1)

# open omero connection
with BlitzGateway(username, password, host=omero_url, port=omero_port, secure=True) as conn:
    for project_name in os.listdir(base_path):
        print(project_name)
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

            os.system("ls " +os.path.join(base_path, project_name, dataset_name))
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