#! /bin/bash
#
# Copyright (c) 2013, 2015 Nicira, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#set -e # exit on first error
#set -x

run() {
    (cd "$sandbox" && "$@") || exit 1
}


builddir=
srcdir=
schema=
installed=true
built=false

ovn=false
controller=false
ovnsb_schema=
ovnnb_schema=
controller_ip="127.0.0.1"
host_ip="127.0.0.1/8"
device="eth0"
index=0

session=false
do_cleanup=false

for option; do
    # This option-parsing mechanism borrowed from a Autoconf-generated
    # configure script under the following license:

    # Copyright (C) 1992, 1993, 1994, 1995, 1996, 1998, 1999, 2000, 2001,
    # 2002, 2003, 2004, 2005, 2006, 2009, 2013 Free Software Foundation, Inc.
    # This configure script is free software; the Free Software Foundation
    # gives unlimited permission to copy, distribute and modify it.

    # If the previous option needs an argument, assign it.
    if test -n "$prev"; then
        eval $prev=\$option
        prev=
        continue
    fi
    case $option in
        *=*) optarg=`expr "X$option" : '[^=]*=\(.*\)'` ;;
        *) optarg=yes ;;
    esac

    case $dashdash$option in
        --)
            dashdash=yes ;;
        -h|--help)
            cat <<EOF
ovs-sandbox, for starting a sandboxed dummy Open vSwitch environment
usage: $0 [OPTION...]

If you run ovs-sandbox from an OVS build directory, it uses the OVS that
you built.  Otherwise, if you have an installed Open vSwitch, it uses
the installed version.

These options force ovs-sandbox to use a particular OVS build:
  -b, --builddir=DIR   specify Open vSwitch build directory
  -s, --srcdir=DIR     specify Open vSwitch source directory
These options force ovs-sandbox to use an installed Open vSwitch:
  -i, --installed      use installed Open vSwitch
  -S, --schema=FILE    use FILE as vswitch.ovsschema
  -o, --ovn            enable OVN
  -c, --controller     enable OVN controller

Other options:
  -h, --help           Print this usage message.
  -c, --controller-ip  The IP of the controller node
  -H, --host-ip        The host ip of the sandbox
  -D, --device         The network device which has the host ip, default is eth0
  -I, --index          The index of sandbox
  -S, --session        Open a bash for running OVN/OVS tools in the
                       dummy Open vSwitch environment
  --cleanup            Cleanup the sandbox, if not controller, the index MUST be
                       specified.
EOF
            exit 0
            ;;

        --b*=*)
            builddir=$optarg
            built=:
            ;;
        -b|--b*)
            prev=builddir
            built=:
            ;;
        --sr*=*)
            srcdir=$optarg
            built=false
            ;;
        -s|--sr*)
            prev=srcdir
            built=false
            ;;
        -i|--installed)
            installed=:
            ;;
        --sc*=*)
            schema=$optarg
            installed=:
            ;;
        -S|--sc*)
            prev=schema
            installed=:
            ;;
        -o|--ovn)
            ovn=true
            ;;
        -c|--controller)
            controller=true;
            ;;
        -I|--index)
            prev=index
            ;;
        -S|--session)
            session=true;
            ;;
        --cleanup)
            do_cleanup=true;
            ;;
        -c|--controller-ip)
            prev=controller_ip
            ;;
        -H|--host-ip)
            prev=host_ip
            ;;
        -D|--device)
            prev=device
            ;;
        -*)
            echo "unrecognized option $option (use --help for help)" >&2
            exit 1
            ;;
        *)
            echo "$option: non-option arguments not supported (use --help for help)" >&2
            exit 1
            ;;
    esac
    shift
done


if $installed && $built; then
    echo "sorry, conflicting options (use --help for help)" >&2
    exit 1
elif $installed || $built; then
    :
elif test -e vswitchd/ovs-vswitchd; then
    built=:
    builddir=.
elif (ovs-vswitchd --version) >/dev/null 2>&1; then
    installed=:
else
    echo "can't find an OVS build or install (use --help for help)" >&2
    exit 1
fi


if $built; then
    if test ! -e "$builddir"/vswitchd/ovs-vswitchd; then
        echo "$builddir does not appear to be an OVS build directory" >&2
        exit 1
    fi
    builddir=`cd $builddir && pwd`

    # Find srcdir.
    case $srcdir in
        '')
            srcdir=$builddir
            if test ! -e "$srcdir"/WHY-OVS.md; then
                srcdir=`cd $builddir/.. && pwd`
            fi
            ;;
        /*) ;;
        *) srcdir=`pwd`/$srcdir ;;
    esac
    schema=$srcdir/vswitchd/vswitch.ovsschema
    if test ! -e "$schema"; then
        echo >&2 'source directory not found, please use --srcdir'
        exit 1
    fi
    if $ovn; then
        ovnsb_schema=$srcdir/ovn/ovn-sb.ovsschema
        if test ! -e "$ovnsb_schema"; then
            echo >&2 'source directory not found, please use --srcdir'
            exit 1
        fi
        ovnnb_schema=$srcdir/ovn/ovn-nb.ovsschema
        if test ! -e "$ovnnb_schema"; then
            echo >&2 'source directory not found, please use --srcdir'
            exit 1
        fi
        vtep_schema=$srcdir/vtep/vtep.ovsschema
        if test ! -e "$vtep_schema"; then
            echo >&2 'source directory not found, please use --srcdir'
            exit 1
        fi
    fi

    # Put built tools early in $PATH.
    if test ! -e $builddir/vswitchd/ovs-vswitchd; then
        echo >&2 'build not found, please change set $builddir or change directory'
        exit 1
    fi
    PATH=$builddir/ovsdb:$builddir/vswitchd:$builddir/utilities:$builddir/vtep:$PATH
    if $ovn; then
        PATH=$builddir/ovn:$builddir/ovn/controller:$builddir/ovn/controller-vtep:$builddir/ovn/northd:$builddir/ovn/utilities:$PATH
    fi
    export PATH
else
    case $schema in
        '')
            for schema in \
                /usr/local/share/openvswitch/vswitch.ovsschema \
                /usr/share/openvswitch/vswitch.ovsschema \
                none; do
                if test -r $schema; then
                    break
                fi
            done
            ;;
        /*) ;;
        *) schema=`pwd`/$schema ;;
    esac
    if test ! -r "$schema"; then
        echo "can't find vswitch.ovsschema, please specify --schema" >&2
        exit 1
    fi
    ovnsb_schema=`dirname $schema`/ovn-sb.ovsschema
    ovnnb_schema=`dirname $schema`/ovn-nb.ovsschema
fi

# Create sandbox.
if $controller; then
    sandbox_name="controller-sandbox"
else
    sandbox_name="sandbox-$index"
fi

sandbox=`pwd`/$sandbox_name


function app_exit {
    local proc=$1
    local pid=

    if [ -f $sandbox/$proc.pid ] ; then
        echo "$proc exit"
        pid=`cat $sandbox/$proc.pid`
        ovs-appctl --timeout 3 -t $sandbox/$proc.$pid.ctl exit || kill $pid
    fi
}


#
# IP related code start
#
declare -a IP_CIDR_ARRAY
declare -A IP_NETMASK_TABLE


function get_ip_cidrs {
    dev=$1

    i=0
    IFS=$'\n'
    #echo "$dev ip cidrs:"
    #echo "---------------------------"
    for inet in `ip addr show $dev | grep -e 'inet\b'` ; do
        local ip_cidr=`echo $inet | \
            sed -n  -e  's%.*inet \(\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}/[0-9]\+\) .*%\1%p'`

        IFS=' '
        read ip_addr netmask <<<$(echo $ip_cidr | sed -e 's/\// /')
        IP_CIDR_ARRAY[i]=$ip_cidr
        IP_NETMASK_TABLE[$ip_addr]=$netmask

        #echo "    cidr $ip_cidr"
        ((i+=1))
    done

    #echo IP_CIDR_ARRAY: ${IP_CIDR_ARRAY[@]}
}


function in_array # ( keyOrValue, arrayKeysOrValues )
{
    local elem=$1

    IFS=' '
    local i
    for i in "${@:2}"; do
        #echo "$i == $elem"
        [[ "$i" == "$elem" ]] && return 0;
    done

    return 1
}


function get_ip_from_cidr {
    local cidr=$1
    echo $cidr | cut -d'/' -f1
}

function get_netmask_from_cidr {
    local cidr=$1
    echo $cidr | cut -d'/' -f2
}


function ip_addr_add {
    local ip=$1
    local dev=$2

    if in_array $ip ${IP_CIDR_ARRAY[@]} ; then
        echo "$ip is already on $dev"
        return
    fi

    echo "Add $ip to $dev"
    sudo ip addr add $ip dev $dev
}


function ip_addr_del {
    local ip=$1
    local dev=$2

    if ! in_array $ip ${IP_CIDR_ARRAY[@]} ; then
        echo "$ip is not on $dev"
        return
    fi

    if [ X"${IP_CIDR_ARRAY[0]}" = X"$ip" ] ; then
        echo "skip main ip $ip on $dev"
        return
    fi

    echo "Delete $ip from $dev"
    sudo ip addr del $ip dev $dev
}

function ip_cidr_fixup {
    local ip=$1
    if [[ ! "$ip" =~ "/" ]] ; then
        echo $ip"/32"
        return
    fi

    echo $ip
}

#
# IP related code end
#
# Get ip addresses on net device
get_ip_cidrs $device
host_ip=`ip_cidr_fixup $host_ip`


function cleanup {

    if [ ! -d $sandbox_name ] ; then
        echo "Not found sandbox $sandbox_name"
        return
    fi

    app_exit ovn-northd
    app_exit ovn-controller
    app_exit ovsdb-server
    app_exit ovs-vswitchd

    # Ensure cleanup.
    pids=`cat "$sandbox_name"/*.pid 2>/dev/null`
    [ -n "$pids" ] && kill -15 $pids

    if $controller; then
        :
    else
        ip_addr_del $host_ip $device
    fi

    rm -rf $sandbox_name
}


if $do_cleanup ; then
    cleanup
    exit 0
fi

cleanup
mkdir $sandbox_name


# Set up environment for OVS programs to sandbox themselves.
OVS_RUNDIR=$sandbox; export OVS_RUNDIR
OVS_LOGDIR=$sandbox; export OVS_LOGDIR
OVS_DBDIR=$sandbox; export OVS_DBDIR
OVS_SYSCONFDIR=$sandbox; export OVS_SYSCONFDIR

cat > $sandbox_name/sandbox.rc <<EOF
OVS_RUNDIR=$sandbox; export OVS_RUNDIR
OVS_LOGDIR=$sandbox; export OVS_LOGDIR
OVS_DBDIR=$sandbox; export OVS_DBDIR
OVS_SYSCONFDIR=$sandbox; export OVS_SYSCONFDIR
EOF


# A UUID to uniquely identify this system.  If one is not specified, a random
# one will be generated.  A randomly generated UUID will be saved in a file
# 'ovn-uuid'.
OVN_UUID=${OVN_UUID:-}

function configure_ovn {
    echo "Configuring OVN"

    if [ -z "$OVN_UUID" ] ; then
        if [ -f $OVS_RUNDIR/ovn-uuid ] ; then
            OVN_UUID=$(cat $OVS_RUNDIR/ovn-uuid)
        else
            OVN_UUID=$(uuidgen)
            echo $OVN_UUID > $OVS_RUNDIR/ovn-uuid
        fi
    fi
}




function start_ovs {
    # Create database and start ovsdb-server.
    echo "Starting OVS"

    touch "$sandbox"/.conf.db.~lock~
    run ovsdb-tool create conf.db "$schema"

    CON_IP=`get_ip_from_cidr $controller_ip`
    echo "controller ip: $CON_IP"

    EXTRA_DBS=""
    OVSDB_REMOTE=""
    if $controller ; then
        if $ovn ; then
            touch "$sandbox"/.ovnsb.db.~lock~
            touch "$sandbox"/.ovnnb.db.~lock~
            run ovsdb-tool create ovnsb.db "$ovnsb_schema"
            run ovsdb-tool create ovnnb.db "$ovnnb_schema"

            ip_addr_add $controller_ip $device

            EXTRA_DBS="ovnsb.db ovnnb.db"
            OVSDB_REMOTE="--remote=ptcp:6640:$CON_IP"
        fi
    fi

    run ovsdb-server --detach --no-chdir --pidfile \
        -vconsole:off --verbose --log-file \
        --remote=punix:"$sandbox"/db.sock \
        $OVSDB_REMOTE \
        conf.db $EXTRA_DBS


    #Add a small delay to allow ovsdb-server to launch.
    sleep 0.1

    #Wait for ovsdb-server to finish launching.
    echo -n "Waiting for ovsdb-server to start..."
    while test ! -e "$sandbox"/db.sock; do
        sleep 1;
    done
    echo "  Done"

    run ovs-vsctl --no-wait -- init
    # Initialize database.
    if $controller ; then
        :
    else

        run ovs-vsctl --no-wait set open_vswitch . system-type="sandbox"

        if $ovn ; then
            OVN_REMOTE="tcp:$CON_IP:6640"

            ip_addr_add $host_ip $device

            run ovs-vsctl --no-wait set open_vswitch . external-ids:system-id="$OVN_UUID"
            ovs-vsctl --no-wait set open_vswitch . external-ids:ovn-remote="$OVN_REMOTE"
            ovs-vsctl --no-wait set open_vswitch . external-ids:ovn-bridge="br-int"
            ovs-vsctl --no-wait set open_vswitch . external-ids:ovn-encap-type="geneve"
            ovs-vsctl --no-wait set open_vswitch . external-ids:ovn-encap-ip="$host_ip"

            ovs-vsctl --no-wait -- --may-exist add-br br-int
            ovs-vsctl --no-wait br-set-external-id br-int bridge-id br-int
            ovs-vsctl --no-wait set bridge br-int fail-mode=secure other-config:disable-in-band=true

            run ovs-vswitchd --detach --no-chdir --pidfile \
                            -vconsole:off --log-file \
                            --enable-dummy=override -vvconn -vnetdev_dummy

        else
            :
        fi
    fi


}


function start_ovn {
    echo "Starting OVN"

    if $controller ; then
        run ovn-northd --detach --no-chdir --pidfile -vconsole:off --log-file
    else
        if $ovn ; then
            run ovn-controller --detach --no-chdir --pidfile -vconsole:off --log-file
        fi
    fi
}


if $ovn ; then
    configure_ovn

    start_ovs

    start_ovn
else
    start_ovs
fi

if ! $session ; then
    exit 0
fi


cat <<EOF

----------------------------------------------------------------------
You are running in a dummy Open vSwitch environment.  You can use
ovs-vsctl, ovs-ofctl, ovs-appctl, and other tools to work with the
dummy switch.

Log files, pidfiles, and the configuration database are in the
"sandbox" subdirectory.

Exit the shell to kill the running daemons.
EOF

status=0; $SHELL || status=$?

cat <<EOF
----------------------------------------------------------------------



EOF

exit $status
