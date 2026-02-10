# Usage Guide

Complete guide for using the Speech-to-Text service.

## Basic Usage

### Starting the Service

```bash
# Activate virtual environment
cd speech-to-text
source venv/bin/activate

# Run with defaults
python cli.py run

# Run with custom config
python cli.py run -c my-config.yaml
```

### Using Speech Recognition

1. **Start Recording**: Press the configured hotkey (default: `Ctrl+Shift+Space`)
2. **Speak**: Talk clearly into your microphone
3. **Stop Recording**: Press the hotkey again
4. **Result**: Text is automatically typed or copied to clipboard

### Stopping the Service

Press `Ctrl+C` in the terminal to stop the service.

## Configuration Examples

### English Transcription with Keyboard Output

```yaml
service:
  language: en
  
output:
  method: keyboard
  
model:
  type: whisper
  path: base
```

### Spanish Transcription with Clipboard

```yaml
service:
  language: es
  
output:
  method: clipboard
  
model:
  type: whisper
  path: small
```

### Catalan Transcription with Both Outputs

```yaml
service:
  language: ca
  
output:
  method: both  # Types AND copies to clipboard
  
model:
  type: whisper
  path: medium
```

## Command-Line Options

### Run Command

```bash
# Basic run
python cli.py run

# With custom config file
python cli.py run -c config.yaml

# Override language
python cli.py run -l es

# Override model
python cli.py run -m small

# Override output method
python cli.py run -o clipboard

# Combine overrides
python cli.py run -l ca -m medium -o both

# Verbose logging
python cli.py run -v
```

### Config Command

```bash
# Create example config
python cli.py config --create

# Create with custom filename
python cli.py config --create -o my-config.yaml

# Show current configuration
python cli.py config --show
```

### Test Command

```bash
# Test all components
python cli.py test

# Test specific component
python cli.py test audio
python cli.py test keyboard
python cli.py test clipboard
```

## Advanced Usage

### Custom Hotkey

Edit `config.yaml`:

```yaml
input:
  hotkey: ctrl+alt+r  # Use Ctrl+Alt+R instead
```

Supported key combinations:
- `ctrl+shift+space`
- `ctrl+alt+s`
- `alt+space`
- `ctrl+shift+r`

### Multiple Languages

To switch between languages, either:

**Option 1**: Edit config and restart
```yaml
service:
  language: es  # Change to desired language
```

**Option 2**: Use command-line override (no restart needed)
```bash
# Stop current service (Ctrl+C)
# Start with different language
python cli.py run -l ca
```

**Option 3**: Run multiple instances with different configs
```bash
# Terminal 1: English
python cli.py run -c config-en.yaml

# Terminal 2: Spanish  
python cli.py run -c config-es.yaml
```

### Adjusting Recording Duration

Edit `config.yaml`:

```yaml
audio:
  max_duration: 60  # Record up to 60 seconds
```

### Using Different Models

#### Faster Processing (Lower Quality)

```yaml
model:
  path: tiny  # Fastest, ~1-2 seconds processing
```

#### Better Accuracy (Slower)

```yaml
model:
  path: large  # Best quality, ~10-20 seconds processing
```

#### Recommended by Use Case

- **Quick notes**: `tiny` or `base`
- **Emails/documents**: `small` or `medium`
- **Professional transcription**: `large`
- **Testing**: `dummy`

## Workflow Examples

### Writing an Email

1. Start service: `python cli.py run -l en -o keyboard`
2. Open email client
3. Click in message body
4. Press hotkey (`Ctrl+Shift+Space`)
5. Dictate your email
6. Press hotkey again
7. Text appears in email

### Taking Notes

1. Start service: `python cli.py run -o clipboard`
2. Open note-taking app
3. Press hotkey to record
4. Speak your notes
5. Press hotkey to stop
6. Paste (`Ctrl+V`) in your app

### Multilingual Document

1. Create configs for each language:
   - `config-en.yaml` (English)
   - `config-es.yaml` (Spanish)
   - `config-ca.yaml` (Catalan)

2. Run with appropriate config:
   ```bash
   # For English section
   python cli.py run -c config-en.yaml
   
   # Stop (Ctrl+C) and switch
   # For Spanish section
   python cli.py run -c config-es.yaml
   ```

### Code Comments/Documentation

Best results with clear speech and technical terms:

```bash
# Use base model for speed
python cli.py run -m base

# In your code editor:
# 1. Position cursor where you want comment
# 2. Type comment prefix (# or //)
# 3. Press hotkey
# 4. Dictate your comment
# 5. Press hotkey
```

## Tips for Best Results

### Speaking Technique

1. **Speak clearly**: Enunciate words
2. **Normal pace**: Not too fast or slow
3. **Reduce background noise**: Use in quiet environment
4. **Good microphone**: Use quality microphone if possible
5. **Pause for punctuation**: Brief pauses help model detect sentences

### Microphone Setup

1. **Position**: 6-12 inches from mouth
2. **Level**: Adjust input volume (not too loud, no clipping)
3. **Test first**: Use `python cli.py test audio`

### Language-Specific Tips

**English**:
- Whisper handles most accents well
- Speak naturally, model adapts

**Spanish**:
- Works well for Latin American and European Spanish
- Specify `language: es` in config

**Catalan**:
- Less training data, may need `medium` or `large` model
- Specify `language: ca` in config

## Troubleshooting

### Common Issues

#### "No transcription result"

**Causes**:
- Recording too short
- No speech detected
- Microphone muted

**Solutions**:
- Speak louder/clearer
- Check microphone settings
- Record longer (at least 1-2 seconds)

#### Incorrect transcription

**Solutions**:
- Use larger model (`small`, `medium`, `large`)
- Speak more clearly
- Reduce background noise
- Check language setting matches speech

#### Hotkey not working

**Solutions**:
- Check if key combo conflicts with other apps
- Try different hotkey combination
- Run with verbose logging: `python cli.py run -v`
- Check terminal for hotkey detection messages

#### Typed text appears delayed

**Solutions**:
- Use smaller/faster model (`tiny`, `base`)
- Ensure system has sufficient resources
- Close unnecessary applications

#### Clipboard not working

**Solutions**:
```bash
# Install clipboard utilities
sudo apt install xclip xsel

# Or use keyboard output instead
python cli.py run -o keyboard
```

## Keyboard Shortcuts Reference

While service is running:

- **Hotkey** (default `Ctrl+Shift+Space`): Start/stop recording
- **Ctrl+C** (in terminal): Stop service

## Performance Tuning

### For Faster Transcription

```yaml
model:
  type: whisper
  path: tiny  # or base

audio:
  max_duration: 15  # Shorter max duration
```

### For Better Accuracy

```yaml
model:
  type: whisper
  path: large  # or medium

audio:
  sample_rate: 16000  # Higher quality
  max_duration: 60    # Longer recordings
```

### For Low-Resource Systems

```yaml
model:
  type: whisper
  path: tiny

audio:
  max_duration: 10
```

## Integration with Other Tools

### With Text Editors

Most text editors work seamlessly:
- VS Code
- Sublime Text
- Atom
- Vim (in insert mode)
- Emacs

### With Office Applications

Compatible with:
- LibreOffice Writer
- Google Docs (browser)
- Microsoft Office (if available)

### With Communication Apps

Works with:
- Slack
- Discord
- Telegram
- Email clients

## Next Steps

- Experiment with different models
- Try all three supported languages
- Create custom configurations for different use cases
- Explore integrating custom STT models (see ARCHITECTURE.md)

## Getting Help

Check logs for detailed error messages:
```bash
# With verbose output
python cli.py run -v

# Check what was captured
# Error messages will show in terminal
```

For more help, see [INSTALL.md](INSTALL.md) and [README.md](README.md).
