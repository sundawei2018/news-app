var client = require('./rpc_client');

// invoke "add"
client.add(1, 2, function(response) {
  console.assert(response == 3);
});


// invoke "getNewsSummariesForUser"
client.getNewsSummariesForUser('test', 2, function(response) {
  console.assert(response != null);
});

// invoke "logNewsClickForUser"
client.logNewsClickForUser('test_user', 'test_news');
