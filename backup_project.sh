#!/bin/bash

# Redactor Project Backup Script
# Creates timestamped backup of entire project

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backup_${TIMESTAMP}"
PROJECT_DIR="/Users/jeremymurray/Projects/redactor/Redactor"

echo "🔄 Starting Redactor Project Backup..."
echo "Timestamp: $TIMESTAMP"
echo "Source: $PROJECT_DIR"
echo "Backup Directory: $BACKUP_DIR"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Copy all Python files
echo "📄 Backing up Python files..."
cp *.py "$BACKUP_DIR/" 2>/dev/null || echo "No Python files found in root"

# Copy configuration files
echo "⚙️ Backing up configuration files..."
cp requirements.txt "$BACKUP_DIR/" 2>/dev/null
cp .env.example "$BACKUP_DIR/" 2>/dev/null
cp *.md "$BACKUP_DIR/" 2>/dev/null
cp *.txt "$BACKUP_DIR/" 2>/dev/null
cp *.sh "$BACKUP_DIR/" 2>/dev/null

# Copy utils directory
if [ -d "utils" ]; then
    echo "🔧 Backing up utils directory..."
    cp -r utils "$BACKUP_DIR/"
fi

# Copy reports directory
if [ -d "reports" ]; then
    echo "📊 Backing up reports directory..."
    cp -r reports "$BACKUP_DIR/"
fi

# Copy development directory
if [ -d "development" ]; then
    echo "🚧 Backing up development directory..."
    cp -r development "$BACKUP_DIR/"
fi

# Copy logs directory
if [ -d "logs" ]; then
    echo "📝 Backing up logs directory..."
    cp -r logs "$BACKUP_DIR/"
fi

# Create inventory of backed up files
echo "📋 Creating backup inventory..."
find "$BACKUP_DIR" -type f | sort > "$BACKUP_DIR/backup_inventory.txt"

# Create project status snapshot
echo "📸 Creating project status snapshot..."
cat > "$BACKUP_DIR/project_status.md" << EOF
# Redactor Project Backup - $TIMESTAMP

## Project Status
- **Backup Date**: $(date)
- **Git Branch**: $(git branch --show-current 2>/dev/null || echo "Not a git repository")
- **Git Commit**: $(git rev-parse HEAD 2>/dev/null || echo "Not a git repository")
- **Project Directory**: $PROJECT_DIR

## Key Features Implemented
- ✅ PDF text extraction and redaction
- ✅ Smart phone number redaction (excludes technical case numbers)
- ✅ Network Team 15-question audit framework
- ✅ OpenAI and Claude AI integration
- ✅ BaseAuditor architecture with shared logic
- ✅ Enhanced performance monitoring
- ✅ Streamlit web interface
- ✅ Batch processing capabilities
- ✅ Comprehensive error handling

## Architecture
- **BaseAuditor**: Shared audit logic and prompt creation
- **OpenAI Auditor**: GPT-4 integration for auditing
- **Claude Auditor**: Claude 3.5 Sonnet integration
- **PDF Parser**: Text extraction and smart redaction
- **GUI**: Streamlit web interface
- **Utils**: Error handling, caching, configuration management

## Recent Changes
- Fixed phone number over-redaction for technical case numbers
- Improved audit report formatting with proper spacing
- Enhanced performance report UI
- Consolidated duplicate code (~500 lines removed)
- Added context-aware redaction patterns

## Files Backed Up
$(wc -l < "$BACKUP_DIR/backup_inventory.txt") files total
EOF

# Create compressed archive
echo "🗜️ Creating compressed archive..."
tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"

# Display backup summary
echo ""
echo "✅ Backup Complete!"
echo "📁 Backup Directory: $BACKUP_DIR"
echo "📦 Compressed Archive: ${BACKUP_DIR}.tar.gz"
echo "📋 Files Backed Up: $(wc -l < "$BACKUP_DIR/backup_inventory.txt")"
echo "💾 Total Size: $(du -sh "$BACKUP_DIR" | cut -f1)"
echo "🗜️ Archive Size: $(du -sh "${BACKUP_DIR}.tar.gz" | cut -f1)"

echo ""
echo "Backup Contents:"
echo "=================="
ls -la "$BACKUP_DIR"

echo ""
echo "🎉 Redactor project successfully backed up!"
