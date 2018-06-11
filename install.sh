if ! [ $(id -u) = 0 ]; then
   echo "This script must be run as root!"
   exit -1
fi

INSTALL="/usr/local/bin"

if [ -z "$1" ]
then
      echo "Notice: Using default install path ($INSTALL)"
else
      INSTALL=$1
fi


cp ./data/org.cunidev.gestures.desktop ./build/org.cunidev.gestures.desktop
sed -e 's|/usr/bin|'$INSTALL'|g' -i ./build/org.cunidev.gestures.desktop  # set .desktop executable path

install -Dm00755 ./build/gestures $INSTALL/gestures
install -Dm00755 ./build/org.cunidev.gestures.desktop /usr/share/applications/org.cunidev.gestures.desktop
install -Dm00755 ./data/org.cunidev.gestures.svg /usr/share/icons/hicolor/scalable/apps/org.cunidev.gestures.svg

echo "Installed to $INSTALL/gestures!"
