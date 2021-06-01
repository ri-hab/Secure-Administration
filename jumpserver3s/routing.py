from channels import route_class, route
from jumpserver3s.consumers import webterminal, SshTerminalMonitor
from guacamole.consumers import GuacamoleWebsocket, GuacamoleMonitor

# The channel routing defines what channels get handled by what consumers,
# including optional matching on message attributes. In this example, we route
# all WebSocket connections to the class-based BindingConsumer (the consumer
# class itself specifies what channels it wants to consume)
channel_routing = [
    route_class(webterminal,path = r'^/ws'),
    route_class(SshTerminalMonitor,path= r'^/monitor/(?P<channel>\w+-\w+-\w+-\w+-\w+-\w+)'),
    route_class(GuacamoleWebsocket,path = r'^/guacamole/(?P<id>[0-9]+)/'),
    route_class(GuacamoleMonitor,path = r'^/guacamolemonitor/(?P<id>[0-9]+)/'),
]
