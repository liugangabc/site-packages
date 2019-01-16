//安装与验证
sudo mkdir /usr/local/java

sudo tar -zxf ~/Downloads/jdk-8u191-linux-x64.tar.gz -C /usr/local/java/

/usr/local/java/jdk1.8.0_191/bin/java -version

# java version "1.8.0_162"
# Java(TM) SE Runtime Environment (build 1.8.0_162-b12)
# Java HotSpot(TM) 64-Bit Server VM (build 25.162-b12, mixed mode)


//配置环境变量等
#sudo vim /etc/profile  //添加以下内容

JAVA_HOME=/usr/local/java/jdk1.8.0_191
PATH=$PATH:$JAVA_HOME/bin:$HOME/bin
export JAVA_HOME
export PATH

#sudo source /etc/profile  //立即生效
#javac -version  //验证
