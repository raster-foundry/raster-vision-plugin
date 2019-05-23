from requests.models import Response


from uuid import UUID


class Experiment(object):
    # TODO: fill in from experiment create non-optional members
    def __init__(self) -> Experiment:
        pass


def create_project(name: str) -> Response:
    """Create a project in the Vision API

    Args:
        name (str): the project to maybe create
    """

    pass


def fetch_project(project_id: UUID) -> Response:
    """Fetch an existing project from the Vision API

    Args:
        project_id (Option[UUID]): the id of the project to fetch
    """

    pass


def create_experiment_for_project(experiment: Experiment, project_id: UUID) -> Response:
    """Create an experiment for an existing project

    Args:
        experiment (Experiment): the experiment json to use in the request body
        project_id (UUID): the id of the project to create this experiment in
    """

    pass
