from omero.gateway import ImageWrapper, DatasetWrapper, ProjectWrapper, BlitzGateway
import omero

def list_projects(conn):
    return conn.getObjects('Project')

def list_datasets_in_project(conn, projectId: int):
    return conn.getObjects('Dataset', opts={'project': projectId})

def list_images_in_dataset(conn, datasetId: int):
    return [image for image in conn.getObjects('Image', opts={'dataset': datasetId})]

def create_project(conn: BlitzGateway, project_name: str) -> ProjectWrapper:
    new_project = ProjectWrapper(conn, omero.model.ProjectI())
    new_project.setName(project_name)
    new_project.save()
    return new_project


def create_dataset(conn: BlitzGateway, projectId: int, dataset_name: str) -> DatasetWrapper:
    # Use omero.gateway.DatasetWrapper:
    new_dataset = DatasetWrapper(conn, omero.model.DatasetI())
    new_dataset.setName(dataset_name)
    new_dataset.save()
    # Can get the underlying omero.model.DatasetI with:
    dataset_obj = new_dataset._obj

    # Create link to project
    link = omero.model.ProjectDatasetLinkI()
    # We can use a 'loaded' object, but we might get an Exception
    # link.setChild(dataset_obj)
    # Better to use an 'unloaded' object (loaded = False)
    link.setChild(omero.model.DatasetI(dataset_obj.id.val, False))
    link.setParent(omero.model.ProjectI(projectId, False))
    conn.getUpdateService().saveObject(link)

    return new_dataset
