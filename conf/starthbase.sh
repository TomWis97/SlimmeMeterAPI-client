#!/usr/bin/env bash
set -e
cd /opt/hbase
/opt/hbase/bin/hbase-config.sh
/opt/hbase/bin/hbase-daemon.sh --config /opt/hbase/conf foreground_start master
