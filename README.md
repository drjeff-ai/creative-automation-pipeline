# 🎨 Creative Automation Pipeline

AI-powered creative asset generation for social media campaigns. Automate the entire workflow from campaign brief to platform-ready creative variations with brand compliance checks.

---

## 🚀 Features

- **AI Image Generation** - Generate product visuals using Flux Pro 1.1
- **Multi-Provider Support** - Extensible architecture for multiple AI services
- **Smart Prompt Engineering** - GPT-4 powered prompt optimization
- **Aspect Ratio Variations** - Automatic generation of 1:1, 9:16, 16:9 formats
- **Brand Compliance** - Automated checks for brand guidelines and legal requirements
- **Text Overlay & Logo Placement** - Professional composition with brand elements
- **Parallel Processing** - Fast generation with concurrent API calls
- **Cost Tracking** - Real-time monitoring of API usage and costs
- **Comprehensive Reporting** - Detailed execution reports with metrics

---

## 📋 Prerequisites

- **Python 3.8+**
- **API Keys:**
  - `FAL_KEY` - fal.ai for Flux Pro image generation
  - `OPENAI_API_KEY` - OpenAI for GPT-4 prompt engineering

---

## ⚡ Quick Start

### **1. Clone & Setup**
```bash
git clone https://github.com/drjeff-ai/creative-automation-pipeline
cd creative-automation-pipeline
pip install -r requirements.txt
```

### **2. Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

### **3. Run Your First Campaign**
```bash
python pipeline.py --brief campaign_briefs/spring_fitness_2025.json
```

### **4. View Results**
```
outputs/
└── quick_test/
    └── test_product/
        ├── 1x1.png    # Square (Instagram feed)
        ├── 9x16.png   # Portrait (Stories/Reels)
        └── 16x9.png   # Landscape (YouTube/Facebook)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│               Campaign Brief (JSON)              │
└────────────────────┬────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │   Pipeline Controller  │
         └───────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼────┐  ┌───▼───┐  ┌────▼─────┐
   │ Prompt  │  │ Asset │  │ Image    │
   │Engineer │  │Manager│  │Generator │
   └────┬────┘  └───┬───┘  └────┬─────┘
        │           │            │
        │           │            │
        └───────────┼────────────┘
                    │
            ┌───────▼────────┐
            │   Creative     │
            │   Composer     │
            └───────┬────────┘
                    │
            ┌───────▼────────┐
            │  Compliance    │
            │   Checker      │
            └───────┬────────┘
                    │
            ┌───────▼────────┐
            │    Output      │
            │   Delivery     │
            └────────────────┘
```

---

## 📁 Project Structure

```
creative-automation-pipeline/
├── pipeline.py                    # Main orchestration script
├── src/
│   ├── asset_manager.py          # File operations & validation
│   ├── image_generator.py        # Image generation orchestration
│   ├── prompt_engineer.py        # AI prompt generation
│   ├── creative_composer.py      # Visual composition & cropping
│   ├── compliance_checker.py     # Brand & legal compliance
│   ├── constants.py              # Centralized constants
│   ├── utils.py                  # Helper utilities
│   └── providers/
│       ├── base.py               # Abstract provider interfaces
│       ├── flux_provider.py      # Flux Pro implementation
│       └── openai_provider.py    # OpenAI GPT-4 implementation
├── campaign_briefs/              # Campaign configuration files
├── input_assets/                 # Brand assets (logos, fonts)
├── outputs/                      # Generated campaign assets
└── requirements.txt              # Python dependencies
```

---

## 🎯 Usage

### **Basic Usage**
```bash
# Generate campaign with default settings
python pipeline.py --brief campaign_briefs/spring_fitness_2025.json

# Verbose logging
python pipeline.py --brief campaign_briefs/spring_fitness_2025.json --verbose

# Skip compliance checks
python pipeline.py --brief campaign_briefs/spring_fitness_2025.json --skip-compliance

# Parallel generation (faster)
python pipeline.py --brief campaign_briefs/spring_fitness_2025.json --parallel
```

### **Campaign Brief Format**
```json
{
  "campaign_id": "spring_fitness_2025",
  "campaign_name": "Spring Transformation Campaign",
  "products": [
    {
      "id": "protein_powder_vanilla",
      "name": "Premium Whey Protein - Vanilla",
      "description": "25g protein, low sugar, smooth vanilla flavor"
    }
  ],
  "region": "north_america",
  "target_audience": "millennials_fitness_enthusiasts",
  "campaign_message": "Transform Your Spring Routine",
  "brand_config": {
    "logo_path": "input_assets/brand/logo.png",
    "primary_color": "#FF5733",
    "secondary_color": "#3498DB",
    "font_color": "#FFFFFF"
  },
  "aspect_ratios": ["1x1", "9x16", "16x9"]
}
```

---

## 🎨 Brand Assets

Place brand assets in organized structure:

```
input_assets/
├── brand/
│   ├── logo.png              # Primary logo
│   └── logo_white.png        # White version (optional)
├── fonts/
│   └── BrandFont-Bold.ttf    # Custom fonts (optional)
└── templates/
    └── background.png        # Templates (optional)
```

---

## 💰 Cost Estimation

**Per Product:**
- Prompt Engineering (GPT-4): ~$0.002
- Image Generation (Flux Pro): $0.055
- **Total per product: ~$0.057**

**Example Campaign (10 products):**
- 10 products × $0.057 = **$0.57**
- 3 aspect ratios per product (included)
- Total creative assets: **30 images**

---

## 🔧 Configuration

### **Environment Variables (.env)**
```bash
# Required
FAL_KEY=your_fal_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional
LOG_LEVEL=INFO
```

### **Aspect Ratio Options**
- `1x1` - Square (1080×1080) - Instagram feed, Twitter
- `9x16` - Portrait (1080×1920) - Instagram/TikTok Stories
- `16x9` - Landscape (1920×1080) - YouTube, Facebook feed
- `4x5` - Portrait (1080×1350) - Instagram portrait
- `2x3` - Portrait (1080×1620) - Pinterest

---


## 📊 Output Structure

```
outputs/
└── campaign_id/
    ├── product_1/
    │   ├── 1x1.png
    │   ├── 9x16.png
    │   └── 16x9.png
    ├── product_2/
    │   ├── 1x1.png
    │   ├── 9x16.png
    │   └── 16x9.png
    ├── compliance_reports/
    │   └── compliance_summary.json
    └── execution_report.json
```

---

## 🛠️ Extending the Pipeline

### **Add a New Image Provider**
```python
# src/providers/my_provider.py
from src.providers.base import ImageProvider

class MyCustomProvider(ImageProvider):
    def generate_image(self, prompt, **kwargs) -> str:
        # Your implementation
        return image_url
```

### **Add Custom Compliance Rules**
```python
# src/compliance_checker.py
def check_custom_rule(self, image_path, campaign_brief):
    # Your validation logic
    return {
        "rule": "custom_rule",
        "status": "pass",
        "details": "Validation details"
    }
```

---

## 🚧 Known Limitations

- **Aspect Ratio Cropping:** Products may be cut off when cropping to different ratios. Center-framing prompts help but aren't perfect.
- **Brand Compliance:** Current compliance checks are basic. Comprehensive brand guideline enforcement requires client-specific configuration.
- **Single Provider:** Currently uses Flux Pro only. Additional providers (DALL-E, Stable Diffusion) can be added via provider interface.
- **Sequential by Default:** Parallel mode available with `--parallel` flag.

---

## 🔮 Future Enhancements

See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for detailed roadmap.

---

## 🐛 Troubleshooting

### **"FAL_KEY not found"**
```bash
# Add to .env file
echo "FAL_KEY=your_key_here" >> .env
```

### **"Image validation failed"**
- Ensure images are PNG/JPG format
- Check minimum resolution (1080×1080)
- Verify file is not corrupted

### **"Budget exceeded"**
- Monitor API usage in execution report
- Use `--skip-generation` to work with existing assets
- Reduce number of products in test campaigns

### **Slow Generation**
- Use `--parallel` flag for concurrent processing
- Check network connection
- Verify API rate limits aren't hit

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is proprietary and confidential.

---

## 👤 Author

**Dr. Jeff** - AI Consultant & Workflow Automation Specialist

---

## 🙏 Acknowledgments

- **Flux Pro (fal.ai)** - Image generation
- **OpenAI GPT-4** - Prompt engineering
- **Anthropic Claude** - Development assistance
- **PIL/Pillow** - Image processing
- **tqdm** - Progress tracking

---

## 💡 Key Design Decisions

### **Provider Abstraction**
Enables swapping AI services without changing core logic. Adding DALL-E or Stable Diffusion requires only implementing the `ImageProvider` interface.

### **Center-Focused Composition**
Empirical testing showed seed-based generation produces inconsistent content across aspect ratios. Center-framing prompts keep products in safe zones for cropping.

### **Centralized Constants**
Single source of truth for aspect ratios, dimensions, and defaults eliminates duplication and ensures consistency.

### **Configuration-Driven**
Campaign briefs in JSON separate business logic from configuration, enabling non-technical users to create campaigns.

---

**Built with ❤️ and AI**
