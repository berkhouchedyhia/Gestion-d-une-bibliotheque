const API_URL = 'http://localhost:5000';

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('fr-FR');
}

function showSection(sectionId) {
    document.querySelectorAll('main > section').forEach(section => {
        section.classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('Chargement initial des données...');
    loadAdherents();
    loadEmprunts();

    const adherentForm = document.getElementById('adherentForm');
    if (adherentForm) {
        console.log("Formulaire d'adhérent trouvé, ajout de l'événement...");
        adherentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log("Soumission du formulaire d'ajout d'adhérent...");
            
            const formData = new FormData(e.target);
            const adherentData = {
                code: formData.get('code'),
                nom: formData.get('nom'),
                prenom: formData.get('prenom'),
                adresse: formData.get('adresse'),
                tel: formData.get('tel'),
                type: formData.get('type')
            };
            console.log('Données envoyées:', adherentData);
            
            try {
                const response = await fetch(`${API_URL}/adherents`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(adherentData)
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    console.error('Erreur API:', errorData);
                    alert(errorData.error || "Erreur lors de l'ajout de l'adhérent");
                    return;
                }
                
                console.log("Adhérent ajouté avec succès!");
                e.target.reset();
                await loadAdherents();
                alert("Adhérent ajouté avec succès!");
            } catch (error) {
                console.error("Erreur lors de la soumission du formulaire:", error);
                alert("Erreur lors de l'ajout de l'adhérent");
            }
        });
    } else {
        console.warn("Attention: Le formulaire d'adhérent n'est pas présent sur cette page.");
    }
});

async function loadAdherents() {
    try {
        console.log('Chargement des adhérents...');
        const response = await fetch(`${API_URL}/adherents`);
        if (!response.ok) throw new Error('Erreur lors du chargement des adhérents');
        const adherents = await response.json();
        console.log('Adhérents reçus:', adherents);
        
        const tbody = document.getElementById('adherentsTable');
        if (tbody) {
            tbody.innerHTML = adherents.map(adherent => `
                <tr>
                    <td>${adherent.code}</td>
                    <td>${adherent.nom}</td>
                    <td>${adherent.prenom}</td>
                    <td>${adherent.type}</td>
                    <td>
                        <button onclick="deleteAdherent(${adherent.id})" class="action-button">Supprimer</button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Erreur de chargement des adhérents:', error);
    }
}

async function loadEmprunts() {
    try {
        console.log('Chargement des emprunts...');
        const response = await fetch(`${API_URL}/emprunts`);
        if (!response.ok) throw new Error('Erreur lors du chargement des emprunts');
        const emprunts = await response.json();
        console.log('Emprunts reçus:', emprunts);
        
        const tbody = document.getElementById('empruntsTable');
        if (tbody) {
            tbody.innerHTML = emprunts.map(emprunt => `
                <tr>
                    <td>${emprunt.nom_adherent} ${emprunt.prenom_adherent}</td>
                    <td>${emprunt.titre_document}</td>
                    <td>${formatDate(emprunt.date_emprunt)}</td>
                    <td>${formatDate(emprunt.date_retour)}</td>
                    <td>${emprunt.status}</td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Erreur de chargement des emprunts:', error);
    }
}
