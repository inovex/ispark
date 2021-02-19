from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, SelectField, FileField, DateField, FloatField, HiddenField, \
    FormField, FieldList, SubmitField, DecimalField, RadioField
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class kernelEnvironment(FlaskForm):

    languageChoices = [('python2', 'python2'), ('python3', 'python3'), ('scala', 'Scala'), ('R', 'R')]


    displayName = StringField(label='Name', id='display_name')
    language = SelectField(label='Select programming language', id='kernel_language', choices=languageChoices)
    extraCondaPackages = StringField(label='Extra Conda packages (separate with comma)', id='extra_conda_packages')
    extraCondaChannels = StringField(label='Conda channels', id='extra_conda_channels')
    extraPIPPackages = StringField(label='Extra PIP packages (separate with comma)', id='extra_pip_packages')

    driverMemory = IntegerField(label='Driver memory (MB)', id='driver_memory', default=2048)
    numExecutors = IntegerField(label='Number of executors', id='num_executors', default=1)
    executorMemory = IntegerField(label='Executor memory (MB)', id='executor_memory', default=2048)
    executorCores = IntegerField(label='Executor cores', id='executor_cores', default=2)

class clusterResourceRules(FlaskForm):

    allowedKernelsNumber = IntegerField(label='Amount of allowed kernels run by one user', id='allowed_num_kernels')


    allowedDriverMemory = IntegerField(label='(MAXIMUM) Driver memory (MB) for creating new kernels', id='allowed_driver_memory')
    allowedNumExecutors = IntegerField(label='(MAXIMUM) Number of executors for creating new kernels', id='allowed_num_executors')
    allowedExecutorMemory = IntegerField(label='(MAXIMUM) Executor memory (MB)  for creating new kernels', id='allowed_executor_memory')
    allowedExecutorCores = IntegerField(label='(MAXIMUM) Executor cores  for creating new kernels', id='allowed_executor_cores')

    defaultDriverMemory = IntegerField(label='(DEFAULT) Driver memory (MB)  for creating new kernels', id='recommended_driver_memory')
    defaultNumExecutors = IntegerField(label='(DEFAULT) Number of executors for creating new kernels', id='recommended_num_executors')
    defaultExecutorMemory = IntegerField(label='(DEFAULT) Executor memory (MB) for creating new kernels', id='recommended_executor_memory')
    defaultExecutorCores = IntegerField(label='(DEFAULT) Executor cores for creating new kernels', id='recommended_executor_cores')

class dummyForm(FlaskForm):

    dummy_field = HiddenField("Field 1")

class modifyRessources(FlaskForm):

    languageChoices = [('python2', 'python2'), ('python3', 'python3'), ('scala', 'Scala'), ('R', 'R')]


    driverMemory = IntegerField(label='Driver memory (MB)', id='driver_memory_mod')
    numExecutors = IntegerField(label='Number of executors', id='num_executors_mod')
    executorMemory = IntegerField(label='Executor memory (MB)', id='executor_memory_mod')
    executorCores = IntegerField(label='Executor cores', id='executor_cores_mod')

class NewForm(FlaskForm):

    kernelEnvironment = FormField(kernelEnvironment)
    dummyForm = FormField(dummyForm)


class NewFormClusterRules(FlaskForm):

    clusterResourceRules = FormField(clusterResourceRules)

class NewFormModifyRessources(FlaskForm):

    modifyRessources = FormField(modifyRessources)