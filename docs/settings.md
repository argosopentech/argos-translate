#### Set package index

Reads package index at https://raw.githubusercontent.com/argosopentech/argospm-index/main/index.json

```
export ARGOS_PACKAGE_INDEX="https://raw.githubusercontent.com/argosopentech/argospm-index/main"
```

#### View debugging information

Argos Translate prints more verbose logging 

```
export ARGOS_DEBUG=1
```

#### Set packages dir
```
export ARGOS_PACKAGES_DIR="/home/user/.local/share/argos-translate/packages/"
```

### Set device
```
export ARGOS_DEVICE_TYPE="cpu"
export ARGOS_DEVICE_TYPE="cuda"
```

### Performance Settings

#### Model precision and quantization
```
export ARGOS_COMPUTE_TYPE="auto"         # Default
export ARGOS_COMPUTE_TYPE="float32"      # Highest accuracy
export ARGOS_COMPUTE_TYPE="int8"         # Fastest, some accuracy loss
export ARGOS_COMPUTE_TYPE="int8_float32" # Best balance of speed/accuracy
```

#### Threading configuration
```
export ARGOS_INTER_THREADS=1       # Number of parallel translators (default: 1)
export ARGOS_INTRA_THREADS=0       # Threads per translator (default: 0 = auto-detect)
```

#### Batch processing
```
export ARGOS_BATCH_SIZE=32         # Translation batch size (default: 32)
```

#### Sentence boundary detection
```
export ARGOS_CHUNK_TYPE="DEFAULT"       # Default behavior
export ARGOS_CHUNK_TYPE="ARGOSTRANSLATE" # Use Argos Translate's SBD
export ARGOS_CHUNK_TYPE="STANZA"        # Use Stanza for sentence splitting
export ARGOS_CHUNK_TYPE="SPACY"         # Use SpaCy for sentence splitting
export ARGOS_CHUNK_TYPE="NONE"          # No sentence splitting
```