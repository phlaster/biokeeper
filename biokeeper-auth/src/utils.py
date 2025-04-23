import ipaddress
from user_agents import  parse

def parse_user_agent(user_agent_string):
    user_agent = parse(user_agent_string)
    return ', '.join(i for i in [
        user_agent.browser.family if user_agent.browser.family != 'Other' else '',
        user_agent.os.family if user_agent.os.family != 'Other' else '',
        user_agent.device.family if user_agent.device.family != 'Other' else ''
    ] if i != '')

def is_internal_ip(ip: str) -> bool:
    # Список сетей, которые используются в Docker Compose (пример)
    internal_ips = [
        ipaddress.ip_address('172.30.0.10'), # core_backend
    ]

    client_ip = ipaddress.ip_address(ip)
    return client_ip in internal_ips