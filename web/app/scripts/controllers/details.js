(function () {
  'use strict';

  angular
    .module('irma')
    .controller('DetailsCtrl', Details);

  Details.$inject = ['$rootScope', '$scope', '$routeParams', 'state', 'resultsManager', '$http', 'FileUploader', 'api'];

  function Details($rootScope, $scope, $routeParams, state, resultManager, $http, FileUploader, api) {
    var vm = this;
    vm.results = undefined;
	$scope.tags = undefined;
    $scope.availableTags = undefined;
    vm.rescan = rescan;
    $scope.file_url = undefined;
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
      });
      
      resultManager.getAvailableTags().then(function(results) {
    	  $scope.availableTags = results.items;
        });
    }
    
    function computeFileURL() {
      var sha256 = vm.results.file_infos.sha256;
      $scope.file_url = sha256.substr(0,2) + "/" + sha256.substr(2,2) + "/" + sha256.substr(4,2) + "/" + sha256;
    }

    function rescan() {
      state.settings.force = true;
      state.newScan();
      addFileToQueue();
      state.lastAction = 'startUpload';
      $scope.$emit('startUpload');
    }

    function addFileToQueue() {
      var url = '/samples/' + $scope.file_url;
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
