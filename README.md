# testplatform
针对app的测试平台


环境依赖：

	1、python3.4+ 【最好是python 3.5.1(之后更新可能会用最新的库)】

	2、appium 1_4_13 +

环境准备：

    1、安装依赖的库：cmd窗口下进入项目目录，执行：pip install -r requirements.txt

	2、等库安装完成后，继续执行命令: python manager.py dbinit   如果输出了 "ok" ，说明环境已经ok

	3、运行目录下的start.bat

	4、打开浏览器访问 http://localhost:5000

使用建议：

    1、先在【设备管理】内添加你的手机信息，设备序号就是deviceName

    2、如果想要跑appium，需要先写测试用例，【用例管理-写测试用例】，api的用法请点击[查看API]按钮；如果想跑monkey性能测试，可以直接去【任务管理-新建任务】(monkey默认跑10000个动作,有点耗时，如果想少跑一点可以改config.py里的monkey_action_count配置项)

    3、有关写测试用例，可以在【用例管理-写测试用例】页点击[打开模拟器],会新开一个mirror的页面，这个是用来在线操作手机，获取元素，保存元素的

        3.1、 mirror用法（1、手机连接到电脑  2、点击页面左上角上传需要测试的app  3、点击[安装并启动app] 之后的操作亲们自己试吧）

        3.2、 建议电脑连接两台手机，一台手机边用mirror保存元素，写用例，另一台手机去跑写好的测试用例

备注：

    1、mirror只在我自己的手机(分辨率为1080*1920)上测试通过，如果发现不好使，可以换个手机试试

    2、由于adb本身不稳定，多次插拔手机会使adb命令出错，导致获取不到手机的连接状态，亲们可以手动重启adb，方式：cmd窗口下执行 adb kill-server  |  adb devices

有关持续集成：

    平台支持与jenkins集成，通过目录下的 jenkins_ci.py  【前提是jenkins部署的机器和本机网络互通】

    1、新建一个jenkins的job，添加Execute Windows batch command,填写如下内容：

        cd $path_to_testplatform

        python jenkins_ci.py $path_to_your_apk all %BUILD_NUMBER% 5000

        说明：$path_to_testplatform 是本地测试平台的存放目录  $path_to_your_apk 是本机待测试apk存放的绝对路径 其他的不需要修改

    2、保存，点击立即构建，此时jenkins会向测试平台发送创建测试任务的请求，在测试平台内会自动新建一个测试任务，默认选择连接正常的手机，以及平台内所有用例设置为通过了的用例进行测试（这就是为什么平台内[所有用例]模块有[设置通过]和[取消通过]按钮，为持续集成设计的）


Doing:

    1、不启动appium获取控件，静态解析app控件树

    2、monkey支持配置action数和动作间隔时间