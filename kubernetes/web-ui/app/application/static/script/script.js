$(function() {
    //flash('It works', 'warning');

    /* Sidebar toggle button */
     $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });

    /*
    Bind Steps Buttons in "add kernel", can be deleted...
    */
    $('#step-1').on('click', function (e) {
        e.preventDefault()
        $('#nav-msi').tab('show')
    })
    $('#step-2,#step-2b').on('click', function (e) {
        e.preventDefault()
        $('#nav-main').tab('show')
    })
    $('#step-3').on('click', function (e) {
        e.preventDefault()
        $('#nav-region').tab('show')
    })


    $('.datetimepicker').datetimepicker({
        locale: 'de'
    });


    // Send Ajax GET Request on showing logs
    $('#modal-show-logs-yarn').on('show.bs.modal', function (e) {
      console.log("YARN-Logs")
      let button = $(e.relatedTarget) // Button that triggered the modal
      var application_id = $(e.relatedTarget).data('application_id');
      let modal = $(this)

      let url = `/cluster/logs/${application_id}`;
      console.log(url)
      $.get(url, function(data, status){
        modal.find('.modal-body').html(data)
      });
    })

        // Send Ajax GET Request on deleting kernel
    $('#modal-delete-kernel').on('show.bs.modal', function (e) {
      let button = $(e.relatedTarget); // Button that triggered the modal
      var folder = $(e.relatedTarget).data('folder');
      let modal = $(this);
      let url = `/kernels/${folder}/delete_kernel`;
      console.log(url)
      $.get(url, function(data, status){
        modal.find('.modal-body').html(data)
      });
    })

     // Send Ajax POST Request on deleting kernel button
    $('#modal-delete-kernel-button').click(function (e) {
      let button = $(this); // Button that triggered the modal
      let modal = $('#modal-delete-kernel');
      let folder = button.data('folder');
      let url = `/kernels/${folder}/delete_kernel`;
      let data = folder;
      var csrf_token = $('#delete-kernel-form').find('input[name="csrf_token"]').val();
      console.log(csrf_token)

      $.ajax({
            type: 'POST',
            url: url,
            headers: {
               "X-CSRFToken": csrf_token,
            },
            data: data,
            success: function(data) {
                submitSuccess(data)
                setTimeout(function () { location.reload(true); }, 1000);
                flash(`Deleting...`, 'success');

            },
            error: function(xhr, status, error) {
                flash(`Error while subbmiting form.`, 'error');

            }
        })
    })

      // Send Ajax GET Request deleting running app
    $('#modal-stop-application-yarn').on('show.bs.modal', function (e) {
      let button = $(e.relatedTarget); // Button that triggered the modal
      var application_id = $(e.relatedTarget).data('application_id');
      let modal = $(this);
      let url = `/cluster/kill_application/${application_id}`;
      console.log(url)
      $.get(url, function(data, status){
        modal.find('.modal-body').html(data)
      });
    })

     // Send Ajax POST Request on deleting running app (button)
    $('#modal-stop-application-yarn-button').click(function (e) {
      let button = $(this); // Button that triggered the modal
      let modal = $('#modal-delete-kernel');
      var application_id = $('#kill-application-form').find('input[name="application_id"]').val();
      let url = `/cluster/kill_application/${application_id}`;
      let data = application_id;
      var csrf_token = $('#kill-application-form').find('input[name="csrf_token"]').val();
      console.log(csrf_token)
      console.log(application_id)

      $.ajax({
            type: 'POST',
            url: url,
            headers: {
               "X-CSRFToken": csrf_token,
            },
            data: data,
            success: function(data) {
                submitSuccess(data)
                setTimeout(function () { location.reload(true); }, 1000);
                flash(`Deleting...`, 'success');

            },
            error: function(xhr, status, error) {
                flash(`Error while subbmiting form.`, 'error');

            }
        })
    })

        // Send Ajax GET Request on modifying resources
    $('#modal-modify-resources').on('show.bs.modal', function (e) {
      let button = $(e.relatedTarget); // Button that triggered the modal
      var folder = $(e.relatedTarget).data('folder');
      var driver_mem = $(e.relatedTarget).data('driver-mem');
      console.log(driver_mem)
      var num_exec = $(e.relatedTarget).data('num-exec');
      var exec_mem = $(e.relatedTarget).data('exec-mem');
      var exec_cores = $(e.relatedTarget).data('exec-cores');
      let modal = $(this)

      let url = `/kernels/${folder}/modify/${driver_mem}/${num_exec}/${exec_mem}/${exec_cores}`;
      console.log(exec_cores)
      $.get(url, function(data, status){
        modal.find('.modal-body').html(data)
      });
    })

        // Send Ajax POST Request on modifying resources button
    $('#modal-modify-resources-button').click(function (e) {
      let button = $(this) // Button that triggered the modal
      let modal = $('#modal-modify-resources');
      let folder = button.data('folder');
      let driver_mem = button.data('driver-mem');
      console.log(driver_mem);
      let num_exec = button.data('num-exec');
      let exec_mem = button.data('exec-mem');
      let exec_cores = button.data('exec-cores');
      let url = `/kernels/${folder}/modify/${driver_mem}/${num_exec}/${exec_mem}/${exec_cores}`;
      let data = $('#modify-resources-form').serialize();

      $.ajax({
            type: 'POST',
            url: url,
            data: data,
            success: function(data) {
                submitSuccess(data)
                setTimeout(function () { location.reload(true); }, 1000);
                flash(`Study description successfuly edited. Page reloading...`, 'success');

            },
            error: function(xhr, status, error) {
                flash(`Error while saving new study description.`, 'error');

            }
        })
    })




});

/*
    Removes a form from the page.
    Shows the buttons from previous form
    @removeId the numeric id of the form to be deleted
    @formNamePrefix the #id PREFIX of the form node
    @formAddPrefix the #id PREFIX of the add button
    @formRemovePrefix the #id PREFIX of the remove button
    @classHidden Class name used to hide elements
*/
const removeForm = function(removeId, formNamePrefix, formAddPrefix, formRemovePrefix, classHidden) {
    // never delete the first form
    if(removeId > 0) {
        //delete form from DOM
        //$(`#${formNamePrefix}${removeId}`).remove();
        $(`#${formNamePrefix}${removeId}`).slideUp(400, function(){
            this.remove();
        });
        //make visible buttons on previous form instance
        $(`#${formAddPrefix}${removeId}`).removeClass(classHidden);
        if(removeId > 1)
            $(`#${formRemovePrefix}${removeId - 1}`).removeClass(classHidden);
    }
}

/*
    Returns a deep clone of a form.
    Increments identifying indices and adjusts headings and buttons.
    Input parameters:
    @nextId the next id used in the cloned form
    @formId the #id of the node to be cloned
    @formAddPrefix the #id PREFIX of the add button
    @formRemovePrefix the #id PREFIX of the remove button
    @classHidden Class name used to hide elements
*/
const cloneForm = function(nextId, formId, formAddPrefix, formRemovePrefix, classHidden) {

    
    oldId = nextId - 1;
    // clone Form
    const newForm = $(`#${formId}`).clone(true, true);
    // increment ids
    newForm.find('[id], [name], [for]').add(newForm).each(function() {
        if(this.id != undefined)
            this.id = this.id.replace(/\d+/, nextId);
        if(this.name != undefined)
            this.name = this.name.replace(/\d+/, nextId);
        if($(this).attr('for') != undefined){
            $(this).attr('for', $(this).attr('for').replace(/\d+/, nextId));
        }
    })
    // rename headings
    newForm.find(':header').each(function() {
        this.innerHTML = this.innerHTML.replace(/\d+/, nextId + 1);
    })
    // increment new add button
    newForm.find(`[id^=${formAddPrefix}]`).each(function() {
        this.id = this.id.replace(/\d+/, nextId + 1);
    })

    // make remove button visible
    newForm.find(`#${formRemovePrefix}${nextId}`).each(function() {
        $(this).removeClass(classHidden);
    })

    // hide buttons on previous instance
    $(`#${formRemovePrefix}${oldId}`).addClass(classHidden);
    $(`#${formAddPrefix}${nextId}`).addClass(classHidden);

    return newForm;
}

/*
    Updates the page after a successful submit & displays success message
    @data Data returned by the AJAX request
*/
const submitSuccess = function(data) {
    console.log(`Success`)
    // hide form to prevent additional submits
    $('#new-form').hide();
    $('#nav-tab').hide();
    // display success message
    $('#alert-success').removeClass('d-none');
    //TODO hook up the progress bar to the file upload status. 
    //TODO If file is uploaded, redirect to home with a simple display alert.
}


/* Displays a dismissable Pop Up Message 
    @message The test of the Message
    @category The message category. Options are:
                info
                success
                warning
                error
            Any other will default to info.
*/
const flash = function(message, category) {
    const msgDiv = $(`#messages`);
    let msgSnippet = `<div class="alert alert-${category} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>`;
    msgDiv.append(msgSnippet);
}
