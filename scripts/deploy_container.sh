set -e

ECR_REGISTRY=${ECR_REGISTRY}
ECR_REPOSITORY=${ECR_REPOSITORY}
IMAGE_TAG=${IMAGE_TAG}

sudo apt-get update

if ! command -v docker &> /dev/null
    then
        echo "Installing Docker..."
        sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
        sudo apt-get update
        sudo apt-get install -y docker-ce
        sudo usermod -aG docker ubuntu
    fi
    
if ! command -v nginx &> /dev/null
    then
        echo "Installing Nginx..."
        sudo apt-get install -y nginx
    fi

if command -v aws &> /dev/null; then
    echo "Installing AWS CLI..."
    sudo apt-get install -y untip
    curl "https://awscli.amazonaws.com/
    awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    fi


if [ ! -f "/etc/nginx/sites-available/streamlit" ]; 
then
  echo "Creating Nginx Configuration..."
  cat > /tmp/streamlit_nginx << 'EOL'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
        proxy_connect_timeout 86400;
        proxy_send_timeout 86400;

        # Fix for ERR_INCOMPLETE_CHUNKED_ENCODING
        proxy_buffering off;
        proxy_buffer_size 16k;
        proxy_busy_buffers_size 24k;
        proxy_buffers 64 4k;

        # Required for Streamlit
        proxy_set_header X-Forwarded-Host $host;
        chunked_transfer_encoding on;
    }

    location /_stcore/stream {
        proxy_pass http://localhost:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;
    }
}
EOL

    sudo cp /tmp/streamlit_nginx /etc/nginx/sites-available/streamlit
    sudo ln -sf /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/streamlit
    sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
    sudo nginx -t
    sudo systemctl restart nginx
fi

echo "Login in to Amazon ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Stop any running container
echo "Stopping any existing container..."
docker stop streamlit-container 2>/dev/null || true
docker rm streamlit-container 2>/dev/null || true
# Pull the latest image
echo "Pulling the latest image from ECR..."
docker pull ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}