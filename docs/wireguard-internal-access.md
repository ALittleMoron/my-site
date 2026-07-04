# WireGuard Internal Access

This project uses host-level WireGuard to reach maintainer-only web panels without
publishing those panels on public HTTPS subdomains.

## Runtime Contract

Public ingress:

- `80/tcp` and `443/tcp` for the edge nginx public site, API, sitemap, robots.txt,
  and public MinIO object endpoint.
- One chosen WireGuard UDP port on the host, for example `51820/udp`.

VPN-only ingress:

- MinIO Console: `http://<VPN_BIND_ADDRESS>:18081`
- Databasus: `http://<VPN_BIND_ADDRESS>:18082`

The production value of `VPN_BIND_ADDRESS` must be the server address on `wg0`,
for example `10.77.0.1`. The `.env.example` value uses `127.0.0.1` so local
development remains safe when WireGuard is not configured.

PostgreSQL, Valkey, backend, frontend, MinIO, and Databasus must not publish
their own Docker ports. nginx remains the only compose service with public port
mappings.

## Host Setup

Install WireGuard on the production host:

```bash
sudo apt update
sudo apt install wireguard
```

Generate keys on the host. Keep private keys out of the repository and out of
logs:

```bash
umask 077
wg genkey | tee server.private | wg pubkey > server.public
wg genkey | tee maintainer-laptop.private | wg pubkey > maintainer-laptop.public
```

Create `/etc/wireguard/wg0.conf` on the server:

```ini
[Interface]
Address = 10.77.0.1/24
ListenPort = 51820
PrivateKey = <server private key>
SaveConfig = false

[Peer]
PublicKey = <maintainer laptop public key>
AllowedIPs = 10.77.0.2/32
```

Protect the server config and start WireGuard:

```bash
sudo chown root:root /etc/wireguard/wg0.conf
sudo chmod 600 /etc/wireguard/wg0.conf
sudo systemctl enable --now wg-quick@wg0
sudo wg show
```

Create the maintainer client config on the maintainer device:

```ini
[Interface]
Address = 10.77.0.2/32
PrivateKey = <maintainer laptop private key>

[Peer]
PublicKey = <server public key>
Endpoint = <server public IP or domain>:51820
AllowedIPs = 10.77.0.1/32
PersistentKeepalive = 25
```

`AllowedIPs` intentionally includes only the server VPN address. Do not route
the maintainer's full internet traffic, Docker subnet, PostgreSQL, or Valkey
through this VPN.

## Firewall Baseline

For a UFW-managed host, keep public ingress narrow and replace `51820` with the
chosen WireGuard UDP port. Before enabling UFW, keep an SSH rule that matches
the current server access policy, or run the change from a provider console:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from <trusted admin IP> to any port 22 proto tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 51820/udp
sudo ufw allow in on wg0 to 10.77.0.1 port 18081 proto tcp
sudo ufw allow in on wg0 to 10.77.0.1 port 18082 proto tcp
sudo ufw enable
sudo ufw status verbose
```

Do not allow `18081/tcp` or `18082/tcp` on the public interface. Docker also
binds those ports to `VPN_BIND_ADDRESS`, so they should not listen on the
server's public IP.

## Deployment

Set the GitHub Actions Environment `production` variable `VPN_BIND_ADDRESS` to
the server's WireGuard address, for example `10.77.0.1`. The CI deploy job runs
after static checks, tests, smoke gates, Docker/image scans, and infrastructure
security checks pass, then waits for manual `production` environment approval.
After approval, it renders `VPN_BIND_ADDRESS` into the runtime `.env` from the
environment manifest before restarting Docker Compose.

After deployment, inspect the nginx bindings on the host:

```bash
docker compose ps nginx
sudo ss -lntp | grep -E ':(80|443|18081|18082)\b'
```

Expected result:

- `80` and `443` are reachable on the public address.
- `18081` and `18082` are bound only to `VPN_BIND_ADDRESS`.

## Peer Revocation

To revoke a maintainer device:

1. Remove that peer block from `/etc/wireguard/wg0.conf`.
2. Remove it from the live interface:

   ```bash
   sudo wg set wg0 peer <revoked peer public key> remove
   sudo wg show
   ```

3. Verify the revoked device can no longer reach:

   ```bash
   curl --connect-timeout 3 http://10.77.0.1:18081
   curl --connect-timeout 3 http://10.77.0.1:18082
   ```

## Acceptance Checks

From a public network without WireGuard:

```bash
curl --connect-timeout 3 http://<server public IP>:18081
curl --connect-timeout 3 http://<server public IP>:18082
curl -kI https://s3-panel.<domain>
curl -kI https://backup.<domain>
```

The first two commands must fail to connect. The old `s3-panel` and `backup`
subdomains must not display MinIO Console or Databasus.

From the maintainer device while connected to WireGuard:

```bash
curl -I http://10.77.0.1:18081
curl -I http://10.77.0.1:18082
```

Both endpoints should reach their web services through nginx.

## References

- WireGuard Quick Start: https://www.wireguard.com/quickstart/
- Docker port publishing: https://docs.docker.com/engine/network/port-publishing/
- UFW documentation: https://help.ubuntu.com/community/UFW
