if (typeof(Storage) !== "undefined") {
    if (localStorage.getItem("I_IP") != null) {
        document.getElementById("RobotIP").value = localStorage.getItem("I_IP");
    } else {
        document.getElementById("RobotIP").value = "localhost";
        localStorage.I_IP = "localhost";
    }
    if (localStorage.getItem("Host") != null) {
        document.getElementById("RobotHost").value = localStorage.getItem("Host");
    } else {
        document.getElementById("RobotHost").value = "9090";
        localStorage.Host = "9090"
    }
} else {
    console.log('Sorry, your browser does not support Web Storage...');
}
//Robot_connnet
var ros = new ROSLIB.Ros({
    url: 'ws://' + document.getElementById("RobotIP").value + ':' + document.getElementById("RobotHost").value
});
//confirm_connect
ros.on('connection', function() {
    console.log('Robot1 Connected to websocket server.');
    websocket_server_msg = 'Robot1 Connected to websocket server.';
    light = "connected";
    context.fillStyle = "green";
    context.fill();
});
ros.on('error', function(error) {
    console.log('Robot1 Error connecting to websocket server: '+ document.getElementById("RobotIP").value);
    websocket_server_msg = 'Robot1 Error connecting to websocket server: '+ document.getElementById("RobotIP").value;
    light = "disconnected";
    context.fillStyle = "red";
    context.fill();
});
ros.on('close', function() {
    console.log('Robot1 Connection to websocket server closed.');
    websocket_server_msg = 'Robot1 Connection to websocket server closed.';
    light = "disconnected";
    context.fillStyle = "red";
    context.fill();
});

function RobotConnect() {
    var IP = document.getElementById("RobotIP").value;
    if (IP != '') {
        localStorage.I_IP = IP;
    } else {
        if (localStorage.getItem("IP") != null) {
            IP = localStorage.getItem("I_IP");
        } else {
            IP = "localhost";
            localStorage.I_IP = "localhost";
        }
    }

    var Host = document.getElementById("RobotHost").value;
    if (Host != '') {
        localStorage.Host = Host;
    } else {
        if (localStorage.getItem("Host") != null) {
            Host = localStorage.getItem("Host");
        } else {
            Host = "9090";
            localStorage.Host = "9090";
        }
    }
    ros = new ROSLIB.Ros({
        url: 'ws://' + IP + ':' + Host
    });
}
var dynaRecClient = new ROSLIB.Service({
    ros : ros,
    name : '/robot1/core/set_parameters',
    serviceType : 'dynamic_reconfigure/Reconfigure'
});


/*
//confirm_connect
ros.on('connection', function() {
    console.log('Robot1 Connected to websocket server.');
    light = "connected";
    context.fillStyle = "green";
    context.fill();
});
ros.on('error', function(error) {
    console.log('Robot1 Error connecting to websocket server:');
    light = "disconnected";
    context.fillStyle = "red";
    context.fill();
});
ros.on('close', function() {
    console.log('Robot1 Connection to websocket server closed.');
    light = "disconnected";
    context.fillStyle = "red";
    context.fill();
});
*/
