(function () {
  'use strict';

  angular
    .module('irma')
    .controller('DetailsCtrl', Details);

  Details.$inject = ['$rootScope', '$scope', '$routeParams', 'state', 'resultsManager', '$http', 'FileUploader', 'api'];

  function Details($rootScope, $scope, $routeParams, state, resultManager, $http, FileUploader, api) {
    var vm = this;
    vm.api = api;
    vm.results = undefined;
	$scope.tags = undefined;
    $scope.availableTags = undefined;
    vm.attachmentList = [];
    vm.rescan = rescan;
    vm.uploader = new FileUploader();
    vm.uploadAttachment = uploadAttachment;
    vm.deleteAttachment = deleteAttachment;
    vm.downloadUrl = undefined;

    $scope.probesDoneButNotExist = new Array();

    $scope.tagAdded = function(tag) {
    	api.tag.addTag(vm.results.file_infos.sha256, tag.id);
    };

    $scope.tagRemoved = function(tag) {
    	api.tag.removeTag(vm.results.file_infos.sha256, tag.id);
    };

    $scope.loadAvailableTags = function(query) {
        var results = [];
        for(var i=0; i < $scope.availableTags.length; i++) {
            if($scope.availableTags[i].text.toLowerCase().indexOf(query.toLowerCase()) > -1) {
                results.push($scope.availableTags[i]);
            }
        }
        return results;
    };


    // Bind uploader events
    this.uploader.onErrorItem = errorUpload;
    this.uploader.onCompleteAll = doneUpload;

    activate();

    function activate() {
      fetchDetails();
    }

    function fetchDetails() {
      if(!state.scan) {
        state.newScan($routeParams.scanId);
      }

      resultManager.getResult($routeParams.resultId).then(function(results) {
        vm.results = results;
        processProbeLists();
        $scope.tags = results.file_infos.tags;
        computeFileURL();
        fetchAttachmentList();
      });
    }

    function fetchAttachmentList() {
      vm.api.file.listAttachments(vm.results.file_infos.sha256).then(function(response) {
        if(response.total > 0) {
          vm.attachmentList = response.data;
        }
      });

      resultManager.getAvailableTags().then(function(results) {
    	  $scope.availableTags = results.items;
        });
    }

    function computeFileURL() {
      var sha256 = vm.results.file_infos.sha256;
      vm.downloadUrl = vm.api.file.downloadUrl(sha256);
    }

    function rescan() {
      state.settings.force = true;
      state.newScan();
      addFileToQueueForRescan();
      state.lastAction = 'startUpload';
      $scope.$emit('startUpload');
    }

    function deleteAttachment(attachment) {
      vm.api.file.deleteAttachment(vm.results.file_infos.sha256, attachment).then(function(response) {
        if(response.total > 0) {
          var index = vm.attachmentList.indexOf(attachment);
          vm.attachmentList.splice(index, 1);
        }
      });
    }

    function uploadAttachment() {
        var items = vm.uploader.getNotUploadedItems();
        _.each(items, function(item){
          item.url = vm.api.file.addAttachments(vm.results.file_infos.sha256);
        });
        vm.uploader.uploadAll();
    }

    function errorUpload() {
      alert("Error when uploading... please retry");
    }

    function doneUpload(event, items) {
      fetchAttachmentList();
    }

    function addFileToQueueForRescan() {
      var url = vm.downloadUrl;
      $http.get(url,{responseType: "blob"})
      .success(function(data, status, headers, config) {
        var mimetype = data.type;
        var file = new File([data], undefined);
        var dummy = new FileUploader.FileItem(state.scan.uploader, {name: vm.results.name, type:mimetype});
        dummy._file = file;
        dummy.progress = 0;
        dummy.isUploaded = false;
        dummy.isSuccess = false;
        state.scan.uploader.queue.push(dummy);
      })
      .error(function(data, status, headers, config) {
        alert("The url could not be loaded...\n (network error? non-valid url? server offline? etc?)");
      });
    }

    function processProbeLists() {
      var probes_done = Array.from(vm.results.probe_list);
      var probes_exist = new Array();

      for (var i=0, item; item = state.probes[i]; i++) {
          probes_exist.push(item.name);
      }

      for (var i=0, item; item = probes_done[i]; i++) {
        if(probes_exist.indexOf(item) < 0) {
          $scope.probesDoneButNotExist.push(item);
        }
      }

      for (var i=0, item; item = state.probes[i]; i++) {
        if(probes_done.indexOf(item.name) < 0) {
          item.active = false;
        } else {
          item.active = true;
        }
      }
    }
  }
}) ();
