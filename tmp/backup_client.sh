#!/bin/bash
rsync -avz -e ssh david@zinn.ddahl.com:/var/backups/ ~/Backups/
