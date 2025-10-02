#!/bin/bash

# Script de déploiement manuel
# Usage: ./deploy.sh

# Configuration
DEPLOY_HOST="votre_vm_ip"
DEPLOY_USER="votre_username"
PROJECT_PATH="/home/$DEPLOY_USER/log430-a25-labo3"
REPO_URL="https://github.com/primika27/log430-a25-labo3.git"

echo "Démarrage du déploiement..."

# Connexion SSH et déploiement
ssh log430@10.194.32.221 << 'ENDSSH'
    set -e  # Arrêt en cas d'erreur
    
    echo "Vérification du projet..."
    if [ -d "$PROJECT_PATH" ]; then
        echo "Mise à jour du code existant..."
        cd $PROJECT_PATH
        git pull origin main
    else
        echo "Clonage initial du repository..."
        git clone $REPO_URL
        cd log430-a25-labo3
    fi
    
    echo "Arrêt des conteneurs existants..."
    docker-compose down || true
    
    echo "Construction et démarrage des nouveaux conteneurs..."
    docker-compose up -d --build
    
    echo "⏳ Attente du démarrage des services..."
    sleep 15
    
    echo "Vérification de l'API..."
    if curl -f http://localhost:5000/health-check; then
        echo "Déploiement réussi !"
    else
        echo "échec du déploiement"
        exit 1
    fi
ENDSSH

echo "Déploiement terminé avec succès !"