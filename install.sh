# install python environment and dependencies
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
# setup systemd service
cp simple_server_mon.template simple_server_mon.service
working_dir=$(echo $PWD)
sed -i "s+script_home+$working_dir+g" "simple_server_mon.service"
sudo cp simple_server_mon.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable simple_server_mon.service
sudo systemctl start simple_server_mon.service