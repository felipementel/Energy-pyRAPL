<div align="center">
  <img src="docs/logo.svg" alt="Energy-pyRAPL Logo" width="200" height="200">
  
  # Energy-pyRAPL
  
  *A Python library for energy consumption monitoring using Intel RAPL (Running Average Power Limit)*
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
</div>

## 🔋 About

Energy-pyRAPL is a Python library that enables developers to monitor and measure energy consumption in their applications using Intel's RAPL (Running Average Power Limit) interface. This tool is essential for:

- **Energy-efficient software development**
- **Green computing initiatives** 
- **Performance optimization with energy awareness**
- **Research in sustainable computing**

## 📊 Features

- Real-time energy consumption monitoring
- Support for different RAPL domains (Package, Core, GPU, Memory)
- Easy-to-use Python API
- Cross-platform compatibility (Linux systems with Intel processors)
- Lightweight and minimal dependencies

## 🚀 Quick Start

```python
import pyrapl

# Initialize energy monitoring
pyrapl.setup()

# Start measuring
measurement = pyrapl.Measurement('my_measurement')
measurement.begin()

# Your code here
# ... energy-intensive operations ...

measurement.end()

# Get results
energy_data = measurement.result
print(f"Energy consumed: {energy_data.pkg} Joules")
```

## 🛠️ Installation

```bash
pip install pyrapl
```

## 📋 Requirements

- Linux operating system
- Intel processor with RAPL support
- Python 3.6 or higher
- Appropriate permissions to access RAPL counters

## 📖 Documentation

For detailed documentation, examples, and API reference, please visit our [documentation](docs/) directory.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [pyRAPL](https://pyrapl.readthedocs.io/) - The original pyRAPL library
- [Intel RAPL](https://software.intel.com/content/www/us/en/develop/articles/intel-power-governor.html) - Intel's Running Average Power Limit technology