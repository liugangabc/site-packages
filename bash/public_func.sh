#!/bin/bash


Validate () {
    # “$#” 会显示传给该函数的参数个数
    # “$@” 会显示所有传给函数的参数

    if [[ ! -n ${1} ]] ;then
        # one not exist
        echo  "validate error"
        exit 1
    fi
}

FileIsExist () {
    Validate ${1}
    if [[ -f ${1} ]];then
        return 0
    else
        echo "FILE ${1} NOT EXIST"
        return 1
    fi
}

PathIsExist() {
    Validate ${1}
    if [[ -d ${1} ]];then
        return 0
    else
        echo "PATH ${1} NOT EXIST"
        return 1
    fi
}


ChooseSystem () {
    # 系统判断
    # radhat或centos存在：/etc/redhat-release 这个文件
    # debian或ubuntu 存在 /etc/debian_version 这个文件
    # lsb_release -a

    if  FileIsExist /etc/redhat-release ; then
        echo "I'm Redhat family"
        YumToDo
        exit 0
    fi
    if  FileIsExist /etc/debian_version ; then
        echo "I'm Debian family"
        AptToDo
        exit 0
    fi
}


YumToDo () {
    echo "yum todo"
}

AptToDo () {
    echo "apt todo"
}

# Main
ChooseSystem
