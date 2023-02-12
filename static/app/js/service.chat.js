'use strict';


angular.module('uetopiaFrontEnd').service('chatService', ['$window', '$q',
  function ($window, $q) {

    var service = {
      chats: [],
      chatchannels: [],
      selected_chat_channel: null,
      append: function (chat) {
        //console.log('chatService appending')
        service.chats.push(chat);
        //console.log(service.chats);
      },
      setChannels: function (channels) {
        service.chatchannels = channels;
        service.selected_chat_channel = channels.length > 0 ? channels[0].key : null;
      },
      send: function (text) {
        var defer = $q.defer();
        gapi.client.chat.create({
          chatChannelKey: service.selected_chat_channel.chatChannelKey,
          text: text
        }).execute(function (resp) {
          console.log('send success', resp.message);
          defer.resolve();
        });
        return defer.promise;
      },
      hasChannel: function (channelKey) {
        return !!_.find(service.chatchannels, {
          chatChannelRefKey: channelKey
        });
      }
    };

    return service;
  }
]);
