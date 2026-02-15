#!/usr/bin/env bash
COMPOSE_OVERRIDE_FILE=./compose.override.yml
ENV_OVERRIDE_FILE=./.env.dev.override
BASH_HISTORY_FILE=./.bash_history
PYTHON_HISTORY_FILE=./.python_history

if [ -f "$COMPOSE_OVERRIDE_FILE" ]; then
    echo "FOUND compose.override.yml"
else
    echo "MISSING compose.override.yml"
    echo ""
    while true; do
        read -p "Do you wish to create it now? " yn
        case $yn in
            [Yy]* ) cp example.compose.override.yml compose.override.yml; break;;
            [Nn]* ) break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
fi

echo ""

if [ -f "$ENV_OVERRIDE_FILE" ]; then
    echo "FOUND .env.dev.override"
else
    echo "MISSING .env.dev.override"
    while true; do
        read -p "Do you wish to create it now? " yn
        case $yn in
            [Yy]* ) touch .env.dev.override; break;;
            [Nn]* ) break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
fi

echo ""

if [ -f "$BASH_HISTORY_FILE" ]; then
    echo "FOUND .bash_history"
else
    echo "MISSING .bash_history"
    echo "Creating .bash_history file..."
    touch "$BASH_HISTORY_FILE"
    echo "Created .bash_history"
fi

echo ""

if [ -f "$PYTHON_HISTORY_FILE" ]; then
    echo "FOUND .python_history"
else
    echo "MISSING .python_history"
    echo "Creating .python_history file..."
    touch "$PYTHON_HISTORY_FILE"
    echo "Created .python_history"
fi

echo ""

if [ -f "$ENV_OVERRIDE_FILE" ] && [ -f "$COMPOSE_OVERRIDE_FILE" ] && [ -f "$BASH_HISTORY_FILE" ] && [ -f "$PYTHON_HISTORY_FILE" ]; then
    echo "All good!"
else
    echo "Not looking good!"
fi
