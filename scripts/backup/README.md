# Backup do Postgres local do Klipper

Roda no servidor, fora do GitHub. O workflow antigo (`backup-db.yml`) não
alcança um banco em rede local, por isso o agendamento dele foi desligado.

## Instalação (uma vez, no servidor)

1. Instalar o `age` (`sudo dnf install age`) e gerar o par de chaves **em outra
   máquina**: `age-keygen -o klipper-backup.key`. Guarde o arquivo `.key` (chave
   privada) fora do servidor e fora do GitHub. Sem ele não há restauração.
2. Criar `~/.config/klipper-backup.env`:

   ```
   BACKUP_DIR=/caminho/do/hd-externo/klipper-backups
   AGE_RECIPIENT=age1...chave-publica...
   ```

3. Testar na mão: `scripts/backup/klipper-backup.sh`
4. Ativar o timer (usuário que roda o Podman):

   ```
   mkdir -p ~/.config/systemd/user
   cp scripts/backup/klipper-backup.{service,timer} ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user enable --now klipper-backup.timer
   loginctl enable-linger "$USER"
   ```

   O `.service` assume o repositório em `~/klipper`; ajuste o `ExecStart` se for outro caminho.

## Restaurar

```
age --decrypt -i klipper-backup.key klipper_AAAAMMDD-HHMMSS.pgdump.age > dump.pgdump
podman exec -i <container-db> pg_restore -U klipper -d klipper_local --clean --if-exists < dump.pgdump
```

Teste a restauração num banco descartável ao menos uma vez.
