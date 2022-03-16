# Microsoft Azure Kinect DK安裝

---

website: [https://docs.microsoft.com/zh-tw/azure/kinect-dk/sensor-sdk-download](https://docs.microsoft.com/zh-tw/azure/kinect-dk/sensor-sdk-download)

1.  設定Microsoft 的套件存放庫

```bash
Ubuntu18.04的安裝方法
1. $ curl -sSL https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
2. $ sudo apt-add-repository https://packages.microsoft.com/ubuntu/18.04/prod
3. $ sudo apt-get update
```

2.  安裝k4a-tools

```bash
$ sudo apt install k4a-tools
```

3.  安裝基本教學課程(版本:1.4)

```bash
$ sudo apt install libk4a1.4-dev
```

4.  下載package

```bash
$ cd catkin_ws/src
$ git clone https://github.com/microsoft/Azure_Kinect_ROS_Driver.git
```

5. **修改 k4a_ros_device.h**

路徑：Azure_Kinect_ROS_Driver/include/azure_kinect_ros_driver/k4a_ros_device.h

```cpp
  *// Last capture timestamp for synchronizing playback capture and imu thread*
       -    std::atomic_int64_t last_capture_time_usec_;
       +    std::atomic<int64_t> last_capture_time_usec_;
 
  *// Last imu timestamp for synchronizing playback capture and imu thread*
       -    std::atomic_uint64_t last_imu_time_usec_;
       -    std::atomic_bool imu_stream_end_of_file_;
       +    std::atomic<uint64_t> last_imu_time_usec_;
       +    std::atomic<bool> imu_stream_end_of_file_;
```

6.  編譯

```bash
$ cd catkin_ws
$ catkin_make
```

7.  測試

```bash
$ roslaunch azure_kinect_ros_driver driver.launch
*# Global Fixed Frame: rgb_camera_link*

$ rostopic list
```

8. 錯誤
1.  

<aside>
💡 To extend the USBFS limit, I manually moddified the grub( **/etc/default/grub** ) chaning ( **GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"** ) to ==> ( **GRUB_CMDLINE_LINUX_DEFAULT="quiet splash usbcore.usbfs_memory_mb=1000"** ),

</aside>

<aside>
💡 Update the grup ( **sudo update-grub** ) and restart your PC ( **sudo reboot** ).

</aside>

<aside>
💡 check if buffer size has successfully changed ( **cat /sys/module/usbcore/parameters/usbfs_memory_mb** )

</aside>

2.  

```powershell
git clone -b v1.2.0 https://github.com/microsoft/Azure-Kinect-Sensor-SDK.git
```

```powershell
sudo cp Azure-Kinect-Sensor-SDK/scripts/99-k4a.rules /etc/udev/rules.d/
```

```powershell
reboot
```
