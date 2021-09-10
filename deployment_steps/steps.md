1. Go to your AWS Management Console and select the EC2 Service.

![s0](https://user-images.githubusercontent.com/50396375/132857453-74d590de-690b-44b6-92e6-3f8b068b9a3e.PNG)

2. Now, from your EC2 Dashboard, click the Launch Instance button.

![s02](https://user-images.githubusercontent.com/50396375/132857539-b7ba21dc-8dfd-4d1b-ab85-6b2950744e06.PNG)

3. Choose an Amazon Machine Image (AMI). For a Graviton2 enabled EC2 instance, select an AMI with 64-bit (Arm). I have chosen Ubuntu Server 18.04 LTS (HVM), SSD Volume Type, 64-bit Arm.

![s1](https://user-images.githubusercontent.com/50396375/132858039-92cdef2c-ed62-4765-bbcc-fde181fb9a86.PNG)

4. Choose an instance type. I have selected the t4g micro instance.

![s2](https://user-images.githubusercontent.com/50396375/132858331-57c75849-cc42-4de8-8cc7-fe948aaa884a.PNG)

5. Click 'Next: Configure Instance Details' 

![s3](https://user-images.githubusercontent.com/50396375/132858859-bf43239a-757e-4f90-ab0e-24be2acfc784.PNG)

and all the following 'Next: ...' buttons until you reach the step called 'Configure Security Group'.
Now, we have to add a Custom TCP Rule for our project. Click the 'Add Rule' button and select the options for the rule as shown in the image below.

![s4](https://user-images.githubusercontent.com/50396375/132859120-1f3efd2c-f717-4113-b45f-120505ae4de4.PNG)

6. Click **Review and Launch**.
![s5](https://user-images.githubusercontent.com/50396375/132859221-5df373de-d253-484f-b5e0-17b8120a6bcd.PNG)

7. Now, click the **Launch** button. In the pop-up window that appears, create a new key pair and download it. This is not to be shared publicly and will be used in later steps.

![s6](https://user-images.githubusercontent.com/50396375/132859599-e57c4d22-e783-4fc9-8952-501ada2b5cda.PNG)

Click **Launch Instances**.

8. Your Graviton2 based instance is now up and running. you can connect to this instance from your local machine using the following command:

```
ssh -i <"key_pair_name">ubuntu@<Your Public DNS Address (IPv4)>
```

9. Execute the following commands:
```
git clone <Repo_HTTPS_URL>
sudo apt update
sudo apt-get install python3-pip
pip3 install Cython
pip3 install --upgrade pip setuptools

sudo apt-get install tmux
cd <Cloned_Repo_Name>
pip3 install -r requirements.txt

tmux new -s StreamSession
streamlit run <filename.py>
```

Now, press **Ctrl + B** _and then_ **D** to keep the website running even if you leave the terminal.

10. Our web application is now ready. You can visit the instances' **IPv4 Public IP** Address to access it. 

![sf](https://user-images.githubusercontent.com/50396375/132866230-106a4558-ffb8-44b5-a518-4fc95e1c382a.PNG)
