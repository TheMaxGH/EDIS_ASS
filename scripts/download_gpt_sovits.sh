#!/bin/bash
# GPT-SoVITS Installation Script
# Автоматическая установка и настройка GPT-SoVITS для EDIS

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running from EDIS_ASSISTANT directory
if [ ! -f "dual_qwen_brain.py" ]; then
    log_error "Please run this script from EDIS_ASSISTANT root directory"
    exit 1
fi

log_info "Starting GPT-SoVITS installation..."

# Step 1: Check dependencies
log_info "Checking dependencies..."

if ! command -v git &> /dev/null; then
    log_error "git is not installed. Please install git first."
    exit 1
fi

if ! command -v python &> /dev/null; then
    log_error "python is not installed. Please install Python 3.10+ first."
    exit 1
fi

if ! command -v ffmpeg &> /dev/null; then
    log_warn "ffmpeg is not installed. Installing..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y ffmpeg
    elif command -v yum &> /dev/null; then
        sudo yum install -y ffmpeg
    else
        log_error "Please install ffmpeg manually"
        exit 1
    fi
fi

log_info "✓ All dependencies are installed"

# Step 2: Clone GPT-SoVITS repository
if [ -d "GPT-SoVITS" ]; then
    log_warn "GPT-SoVITS directory already exists. Skipping clone."
else
    log_info "Cloning GPT-SoVITS repository..."
    git clone https://github.com/RVC-Boss/GPT-SoVITS.git
    log_info "✓ Repository cloned"
fi

cd GPT-SoVITS

# Step 3: Install Python dependencies
log_info "Installing Python dependencies..."
pip install -r requirements.txt
log_info "✓ Dependencies installed"

# Step 4: Download pretrained models
log_info "Downloading pretrained models..."

mkdir -p pretrained_models

# GPT model
if [ ! -f "pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt" ]; then
    log_info "Downloading GPT model..."
    wget -O pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt \
        "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s1bert25hz-2kh-longer-epoch%3D68e-step%3D50232.ckpt"
else
    log_info "✓ GPT model already downloaded"
fi

# SoVITS model
if [ ! -f "pretrained_models/s2G488k.pth" ]; then
    log_info "Downloading SoVITS model..."
    wget -O pretrained_models/s2G488k.pth \
        "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s2G488k.pth"
else
    log_info "✓ SoVITS model already downloaded"
fi

# BERT models
log_info "Downloading BERT models..."
mkdir -p pretrained_models/chinese-roberta-wwm-ext-large
mkdir -p pretrained_models/chinese-hubert-base

if [ ! -f "pretrained_models/chinese-roberta-wwm-ext-large/pytorch_model.bin" ]; then
    log_info "Downloading Chinese RoBERTa..."
    cd pretrained_models/chinese-roberta-wwm-ext-large
    wget https://huggingface.co/hfl/chinese-roberta-wwm-ext-large/resolve/main/pytorch_model.bin
    wget https://huggingface.co/hfl/chinese-roberta-wwm-ext-large/resolve/main/config.json
    cd ../..
else
    log_info "✓ Chinese RoBERTa already downloaded"
fi

log_info "✓ All models downloaded"

# Step 5: Create necessary directories
cd ..
log_info "Creating directories..."
mkdir -p audio_cache/references
mkdir -p models/voice
mkdir -p logs
log_info "✓ Directories created"

# Step 6: Test installation
log_info "Testing installation..."
cd GPT-SoVITS

python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
    print(f'GPU 6: {torch.cuda.get_device_name(6) if torch.cuda.device_count() > 6 else \"Not available\"}')
"

cd ..

log_info "✓ Installation test passed"

# Step 7: Create startup script
log_info "Creating startup script..."
cat > start_gpt_sovits.sh << 'EOF'
#!/bin/bash
# Start GPT-SoVITS TTS Server

export CUDA_VISIBLE_DEVICES=6

cd GPT-SoVITS
python api.py --port 9880
EOF

chmod +x start_gpt_sovits.sh
log_info "✓ Startup script created"

# Final message
echo ""
echo "=========================================="
log_info "GPT-SoVITS installation completed!"
echo "=========================================="
echo ""
echo "To start the TTS server:"
echo "  ./start_gpt_sovits.sh"
echo ""
echo "Or use the full system launcher:"
echo "  python run_system.py"
echo ""
echo "API will be available at: http://localhost:9880"
echo "=========================================="
