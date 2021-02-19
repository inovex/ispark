from flask import request
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
"""
Template Processor: "Remembers" the navigation trail to the current node in the file tree.
Returns a dict with four entries:
projectId, studyId, datasetId, regionId
If not applicable, every entry defaults to none.
"""
