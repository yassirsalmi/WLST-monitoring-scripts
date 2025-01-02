import os
import sys
from java.lang import System

def healthstat(server_name):
    try:
        cd('/ServerRuntimes/' + server_name + '/ThreadPoolRuntime/ThreadPoolRuntime')
        health_state = get('HealthState')
        return health_state.toString().split(',')[2].split(':')[1].split('HEALTH_')[1]
    except:
        return 'UNKNOWN'

def monitor_server_status(fo):
    domainRuntime()
    servers = domainRuntimeService.getServerRuntimes()
    fo.write('<h2>SERVER STATUS REPORT</h2>')
    fo.write('<table border="1" style="width:100%">')
    fo.write('<tr bgcolor="#4477BB"><th>Server Name</th><th>Status</th><th>Health</th></tr>')
    
    for server in servers:
        status = server.getState()
        health = healthstat(server.getName())
        
        status_color = '#90EE90' if status == 'RUNNING' else '#FFB6C6'
        health_color = '#90EE90' if health == 'OK' else '#FFFF00' if health == 'WARN' else '#FFB6C6'
        
        fo.write('<tr bgcolor="#F4F6FA">')
        fo.write('<td>%s</td>' % server.getName())
        fo.write('<td bgcolor="%s">%s</td>' % (status_color, status))
        fo.write('<td bgcolor="%s">%s</td>' % (health_color, health))
        fo.write('</tr>')
    fo.write('</table>')

def monitor_heap_usage(fo):
    fo.write('<h2>SERVER HEAP SIZE REPORT</h2>')
    fo.write('<table border="1" style="width:100%">')
    fo.write('<tr bgcolor="#4477BB"><th>Managed Server</th><th>HeapFreeCurrent</th><th>HeapSizeCurrent</th><th>HeapFreePercent</th></tr>')
    
    servers = domainRuntimeService.getServerRuntimes()
    for server in servers:
        cd('/ServerRuntimes/%s/JVMRuntime/%s' % (server.getName(), server.getName()))
        heap_free = float(get('HeapFreeCurrent')) / (1024 * 1024)
        heap_size = float(get('HeapSizeCurrent')) / (1024 * 1024)
        heap_free_pct = float(get('HeapFreePercent'))
        
        bgcolor = '#F4F6FA'
        if heap_free_pct <= 20:
            bgcolor = '#FFFF00' if heap_free_pct > 10 else '#FFB6C6'
            
        fo.write('<tr bgcolor="%s">' % bgcolor)
        fo.write('<td>%s</td>' % server.getName())
        fo.write('<td>%.2f MB</td>' % heap_free)
        fo.write('<td>%.2f MB</td>' % heap_size)
        fo.write('<td>%.1f%%</td>' % heap_free_pct)
        fo.write('</tr>')
    fo.write('</table>')

def monitor_jdbc(fo):
    fo.write('<h2>SERVER JDBC RUNTIME INFORMATION</h2>')
    servers = domainRuntimeService.getServerRuntimes()
    
    for server in servers:
        fo.write('<h3>%s</h3>' % server.getName())
        fo.write('<table border="1" style="width:100%">')
        fo.write('<tr bgcolor="#4477BB"><th>Data Source</th><th>State</th><th>Active Connections</th><th>Waiting for Connections</th></tr>')
        
        try:
            jdbc_runtime = server.getJDBCServiceRuntime()
            datasources = jdbc_runtime.getJDBCDataSourceRuntimeMBeans()
            
            for ds in datasources:
                state_color = '#FFB6C6' if ds.getState() != "Running" else '#F4F6FA'
                active_conn = ds.getActiveConnectionsCurrentCount()
                waiting_conn = ds.getWaitingForConnectionCurrentCount()
                
                fo.write('<tr bgcolor="%s">' % state_color)
                fo.write('<td>%s</td>' % ds.getName())
                fo.write('<td>%s</td>' % ds.getState())
                fo.write('<td>%d</td>' % active_conn)
                fo.write('<td>%d</td>' % waiting_conn)
                fo.write('</tr>')
        except:
            fo.write('<tr><td colspan="4">No JDBC resources found</td></tr>')
        fo.write('</table>')

def monitor_jms(fo):
    fo.write('<h2>SERVER JMS STATUS INFORMATION</h2>')
    servers = domainRuntimeService.getServerRuntimes()
    
    for server in servers:
        fo.write('<h3>JMS Runtime Info for: %s</h3>' % server.getName())
        fo.write('<table border="1" style="width:100%">')
        fo.write('''<tr bgcolor="#4477BB">
            <th>SERVER</th>
            <th>JMSSERVER</th>
            <th>DestinationName</th>
            <th>DestinationType</th>
            <th>MessagesCurrentCount</th>
            <th>MessagesHighCount</th>
            <th>ConsumersCurrentCount</th>
            <th>ConsumersHighCount</th>
            <th>ConsumersTotalCount</th>
            </tr>''')
        
        try:
            jms_runtime = server.getJMSRuntime()
            jms_servers = jms_runtime.getJMSServers() if jms_runtime else []
            
            if jms_servers and len(jms_servers) > 0:
                row_count = 0
                for jms_server in jms_servers:
                    destinations = jms_server.getDestinations()
                    if destinations and len(destinations) > 0:
                        for dest in destinations:
                            bgcolor = '#F4F6FA' if row_count % 2 == 0 else '#E6E6FA'
                            dest_name = dest.getName()
                            
                            fo.write('<tr bgcolor="%s">' % bgcolor)
                            fo.write('''<td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%d</td>
                                <td>%d</td>
                                <td>%d</td>
                                <td>%d</td>
                                <td>%d</td>''' % (
                                server.getName(),
                                jms_server.getName(),
                                dest_name,
                                dest.getDestinationType(),
                                dest.getMessagesCurrentCount(),
                                dest.getMessagesHighCount(),
                                dest.getConsumersCurrentCount(),
                                dest.getConsumersHighCount(),
                                dest.getConsumersTotalCount()
                            ))
                            fo.write('</tr>')
                            row_count += 1
                    else:
                        fo.write('<tr bgcolor="#F4F6FA">')
                        fo.write('''<td>%s</td>
                            <td>%s</td>
                            <td colspan="7">No destinations found for this JMS server</td>''' % (
                            server.getName(),
                            jms_server.getName()
                        ))
                        fo.write('</tr>')
            else:
                fo.write('<tr bgcolor="#F4F6FA">')
                fo.write('''<td>%s</td>
                    <td colspan="8">No JMS servers found</td>''' % server.getName())
                fo.write('</tr>')
                
        except Exception as e:
            fo.write('<tr bgcolor="#F4F6FA">')
            fo.write('''<td>%s</td>
                <td colspan="8">Error retrieving JMS information: %s</td>''' % (
                server.getName(),
                str(e)
            ))
            fo.write('</tr>')
        
        fo.write('</table>')

def get_jms_destination_path(server_name, jms_server_name, destination_name):
    """Helper function to construct the full JMS destination path"""
    try:
        domainConfig()
        servers = cmo.getJMSServers()
        for server in servers:
            if server.getName() == jms_server_name:
                module_name = server.getTargets()[0].getName()
                return 'UMSJMSSystemResource/%s/%s/%s' % (
                    module_name,
                    jms_server_name,
                    destination_name
                )
    except:
        return destination_name
    return destination_name

def main():
    if len(sys.argv) < 3:
        print("Usage: wlst.sh monitor_all_servers.py <server> <port>")
        sys.exit(1)
        
    try:
        connect('webLogic', '01100119', 't3://%s:%s' % (sys.argv[1], sys.argv[2]))
        
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        output_file = os.path.join(script_dir, 'monitorstatus.html')
        
        with open(output_file, 'w') as fo:
            fo.write('''<html><head><style>
                table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                th, td { padding: 8px; text-align: center; border: 1px solid #ddd; }
                th { color: white; }
                h2 { color: #333366; }
                </style></head><body>''')
            fo.write('<h1>SERVER STATUS REPORT: t3://%s:%s</h1>' % (sys.argv[1], sys.argv[2]))
            monitor_server_status(fo)
            monitor_heap_usage(fo)
            monitor_jdbc(fo)
            monitor_jms(fo)
            fo.write('</body></html>')
            
        print("Report generated at: %s" % output_file)
    except Exception as e:
        print("Error: %s" % str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
