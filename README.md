## 1) Выкачивает все пакеты docker из docker-registry

### Сделано автоматика по выкачке, чтобы руками не указываь версию и папку куда загрузить.

задержка 10 секунд для обхода лимита. 

если не обойдет, то перезапукстить еще раз оно продолжить качать

запоминает что скачалось в success.txt



Плюсы: качает каждую секцию  из Dockerfile из RUN - разные действия в разных папках *.tar.gz
например:
не надо по готовому или запущенному образу docker рыться во всех фаилах и искать что изменилось
1) первом действии качается alpine:latest - смысла изучать нам его нет
2) копируются сертификаты ssl или id_rsa в отдельные папки. Вот чтоб их не искать они будут в отдельном действии в *.tar.gz

### INSTALL

```
pip2.7 install -r requirements.txt 
```


###  Docker Registry

проверка https://docker-registry.SITE.com:5000/v2/_catalog

```
python2.7 docker_image_fetch.py -u https://docker-registry.SITE.com:5000
```

###  Sonatype Nexus Repository Manager

проверка https://repo.SITE.com/repository/docker-repo/v2/_catalog

```
python2.7 docker_image_fetch.py -u https://repo.SITE.com/repository/docker-repo/
```

структура каталогов tree

```
├── php
│   ├── 5.7
│   |   ├── ....
│   ├── 7.1
│   |   ├── ...
│   ├── 7.2
│   └── latest
│   |   ├── 027f9c83eab21c70c02c6dad37498e0aa46989545d413ec341d740a093df357d.tar.gz # фаилы ssl или id_rsa из Dockerfile из секции RUN
│   |   ├── 027f9c83eab21c70c02c6dad37498e0aa46989545d413ec341d740a093df357d.tar.gz
│   │   ├── manifests.json # все действия происходящие в Dockerfile
│   │   └── success.txt # скачано успешно
│   ├── success.txt # скачано успешно полностью
│   └── tags.json # все теги которые есть для выкачивания
```

распаковать фаилы
```
# .tar.gz
find . -name '*.tar.gz' -exec tar -zxvf  {} \;

# APK
find . -type f -name '*.apk' -execdir apktool d  {} \;

#RPM
find .  -type f -iname "*.rpm" -exec sh -c 'f=$(basename $1 .rpm);d=$(dirname $1);echo "$d/$f";rpm2cpio {}  | cpio -D "$d/$f" -idmv' sh {} \;

# ZIP
find .  -type f -name "*.zip" -execdir sh -c 'f=$(basename $1 .zip);d=$(dirname $1);echo "$d/$f";unzip -d "$d/$f" $f' sh {} \;

# TGZ
find .  -type f -name "*.tgz" -execdir sh -c 'f=$(basename $1 .tgz);d=$(dirname $1);echo "$d/$f";mkdir -p "$d/$f";tar zxvf $1 -C ./"$d/$f" ' sh {} \;

# nuget .nupkg
find .  -type f -name "*.nupkg" -execdir sh -c 'f=$(basename $1 .nupkg);d=$(dirname $1);echo "$d/$f";unzip -d "$d/$f" $1' sh {} \;

# pip install wheel
find .  -type f -name "*.whl" -execdir sh -c 'f=$(basename $1 .whl);d=$(dirname $1);echo "$d/$f";wheel unpack -d "$d/$f" $1' sh {} \;

# decompile .jar .class
find .  -type f -iname "*.jar" -exec sh -c 'f=$(basename $1 .jar);d=$(dirname $1);echo "$d/$f";unzip -d $1.tmp $1' sh {} \;
find .  -type f -iname "*.class" -execdir sh -c 'f=$(basename $1 .jar);d=$(dirname $1);echo "$d/$f";jad -d $(dirname $f) -s java -lnc $f' sh {} \;
```


ищем

```
find . -name '*.json' -exec grep -i 'password' {} \; -print
find . -type f -name 'id_rsa' -o -name "auth.json"  -o -name "config.json" 
```


## 2) Выкачивает все пакеты из Sonatype Nexus Repository Manager

NPM, bower, composer, nuget, pypi, yum, raw

PS пакеты докера выкачивать через docker_image_fetch.py

проверка https://repo.SITE.com/service/rest/v1/repositories

```
python2.7 sonatype_nexus_image_fetch.py -u https://repo.SITE.com/service/rest/v1/repositories
```

