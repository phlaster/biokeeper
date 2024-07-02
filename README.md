# <img src="assets/biokeeper_logo.png" width="2%"> Biokeeper
Citizen science biosample annotation tool

<table>
  <tr>
    <td><img src="assets/pic4.svg" width=150 height=150></td>
    <td><img src="assets/pic3.svg" width=150 height=150></td>
    <td><img src="assets/pic5.svg" width=150 height=150></td>
    <td><img src="assets/pic6.svg" width=150 height=150></td>
    <td><img src="assets/pic1.svg" width=150 height=150></td>
    <td><img src="assets/pic7.svg" width=150 height=150></td>
    <td><img src="assets/pic8.svg" width=150 height=150></td>
  </tr>
 </table>

# For users
## Project structure
### Repositories
The __Biokeeper__ project file structure organized into several submodules for ease of development several logical parts of the project. Currently they are:
```sh
biokeeper # this repo, contains common docker-compose.yml to start all the server-side services
├── biokeeper-admin    # admin web page
├── biokeeper-auth     # users authentication service
├── biokeeper-backend  # core server-side application logic
└── biokeeper-frontend # ReactJS cross-platform app
```
### Microservice architecture
<img src="assets/biokeeper_architecture_diagram.svg" width=70% height=400>

## Start of work
First you need to clone this repo with all the submodues:
```sh
git clone --recurse-submodules git@github.com:phlaster/biokeeper.git
cd biokeeper
```
Then make sure you put relevant JWT public and private keys into `jwt_keys/` directory and feel free to run:
```sh
docker-compose build
docker-compose up
```

# For developers
## Setting up GIT
To work on this or any child repo you need:

1. Set up your git credentials (where `USERNAME` is your user name):
    ```sh
    git config --global user.name "USERNAME"
    git config --global user.email USERNAME@users.noreply.github.com
    ```

2. In GitHub web UI __FORK CHOSEN REPO__.

3. Clone the repo to your local machine:
    ```sh
    git clone git@github.com:USERNAME/REPONAME.git
    cd REPONAME
    ```

4. Explicitly set `upstream`:
    ```sh
    git remote add upstream git@github.com:phlaster/REPONAME.git
    ```

5. Check that everything is as expected:
    ```sh
    git remote -v
    ```
    You should see something like:
    ```sh
    origin	git@github.com:USERNAME/REPONAME.git (fetch)
    origin	git@github.com:USERNAME/REPONAME.git (push)
    upstream	git@github.com:phlaster/REPONAME.git (fetch)
    upstream	git@github.com:phlaster/REPONAME.git (push)
    ```

6. Fetch updates from `upstream` repo:
    ```sh
    git fetch upstream
    ```

7. Merge updates with the branch of your choice:
    ```sh
    git checkout master
    git merge upstream/master
    # OR
    git checkout dev
    git merge upstream/dev
    ```
8. Then after work is done push changes into your personal repo:
    ```sh
    git push origin master
    # OR
    git push origin dev
    ```

# Contributors
<table>
<tr>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/Mityamops>
            <img src=https://avatars.githubusercontent.com/u/125828608?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Mityamops/>
            <br />
            <sub style="font-size:14px"><b>Mityamops</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/Momochka>
            <img src=https://avatars.githubusercontent.com/u/125281818?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Momochka/>
            <br />
            <sub style="font-size:14px"><b>Momochka</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/kiriklzz>
            <img src=https://avatars.githubusercontent.com/u/112094641?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=kiriklzz/>
            <br />
            <sub style="font-size:14px"><b>kiriklzz</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/Rimk4>
            <img src=https://avatars.githubusercontent.com/u/82030462?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Rimk4/>
            <br />
            <sub style="font-size:14px"><b>Rimk4</b></sub>
        </a>
    </td>
</tr>
<tr>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/arprspb>
            <img src=https://avatars.githubusercontent.com/u/147101890?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=arprspb/>
            <br />
            <sub style="font-size:14px"><b>arprspb</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/d3biruwan>
            <img src=https://avatars.githubusercontent.com/u/91975865?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=d3biruwan/>
            <br />
            <sub style="font-size:14px"><b>d3biruwan</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/Lo-Lap>
            <img src=https://avatars.githubusercontent.com/u/116972772?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=Lo-Lap/>
            <br />
            <sub style="font-size:14px"><b>Lo-Lap</b></sub>
        </a>
    </td>
    <td align="center" style="word-wrap: break-word; width: 150.0; height: 150.0">
        <a href=https://github.com/phlaster>
            <img src=https://avatars.githubusercontent.com/u/125278254?v=4 width="100;"  style="border-radius:50%;align-items:center;justify-content:center;overflow:hidden;padding-top:10px" alt=phlaster/>
            <br />
            <sub style="font-size:14px"><b>phlaster</b></sub>
        </a>
    </td>
</tr>
</table>
