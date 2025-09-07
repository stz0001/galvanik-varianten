<?php
require_once '../config.php';

$pdo = getDB();

// Get selected anlage from query parameter
$selected_anlage = isset($_GET['anlage']) ? $_GET['anlage'] : 'alle';
$search = isset($_GET['search']) ? $_GET['search'] : '';

// Build query
$query = "SELECT * FROM codes WHERE 1=1";
$params = [];

if ($selected_anlage !== 'alle') {
    $query .= " AND anlage = :anlage";
    $params['anlage'] = $selected_anlage;
}

if ($search) {
    $query .= " AND (code LIKE :search OR vb_text ILIKE :search2 OR hb_text ILIKE :search3 OR pas_text ILIKE :search4 OR nb_text ILIKE :search5)";
    $searchTerm = '%' . $search . '%';
    $params['search'] = $searchTerm;
    $params['search2'] = $searchTerm;
    $params['search3'] = $searchTerm;
    $params['search4'] = $searchTerm;
    $params['search5'] = $searchTerm;
}

$query .= " ORDER BY anlage, code";

$stmt = $pdo->prepare($query);
$stmt->execute($params);
$codes = $stmt->fetchAll();

// Get statistics
$stats_query = "SELECT anlage, COUNT(*) as code_count, SUM(artikel_count) as artikel_total FROM codes GROUP BY anlage ORDER BY anlage";
$stats = $pdo->query($stats_query)->fetchAll();

// Export CSV if requested
if (isset($_GET['export']) && $_GET['export'] === 'csv') {
    header('Content-Type: text/csv');
    header('Content-Disposition: attachment; filename="varianten_export.csv"');
    
    $output = fopen('php://output', 'w');
    fputcsv($output, ['Anlage', 'Code', 'VB', 'VB Text', 'HB', 'HB Text', 'PAS', 'PAS Text', 'NB', 'NB Text', 'Artikel']);
    
    foreach ($codes as $row) {
        fputcsv($output, [
            $row['anlage'],
            $row['code'],
            $row['vb'],
            $row['vb_text'],
            $row['hb'],
            $row['hb_text'],
            $row['pas'],
            $row['pas_text'],
            $row['nb'],
            $row['nb_text'],
            $row['artikel_count']
        ]);
    }
    
    fclose($output);
    exit;
}
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Variantenexplorer</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>Variantenexplorer</h1>
        
        <div class="stats">
            <?php foreach ($stats as $stat): ?>
                <div class="stat-card">
                    <h3><?php echo htmlspecialchars($stat['anlage'] === 'A6' ? 'A60' : $stat['anlage']); ?></h3>
                    <p><?php echo $stat['code_count']; ?> Codes</p>
                    <p><?php echo number_format($stat['artikel_total'], 0, ',', '.'); ?> Artikel</p>
                </div>
            <?php endforeach; ?>
        </div>
        
        <div class="controls">
            <form method="GET" action="">
                <select name="anlage" onchange="this.form.submit()">
                    <option value="alle" <?php echo $selected_anlage === 'alle' ? 'selected' : ''; ?>>Alle Anlagen</option>
                    <option value="G2" <?php echo $selected_anlage === 'G2' ? 'selected' : ''; ?>>G2</option>
                    <option value="G3" <?php echo $selected_anlage === 'G3' ? 'selected' : ''; ?>>G3</option>
                    <option value="G4" <?php echo $selected_anlage === 'G4' ? 'selected' : ''; ?>>G4</option>
                    <option value="G5" <?php echo $selected_anlage === 'G5' ? 'selected' : ''; ?>>G5</option>
                    <option value="A6" <?php echo $selected_anlage === 'A6' ? 'selected' : ''; ?>>A60</option>
                </select>
                
                <input type="text" name="search" placeholder="Suche..." value="<?php echo htmlspecialchars($search); ?>">
                <button type="submit">Suchen</button>
                
                <a href="?anlage=<?php echo $selected_anlage; ?>&search=<?php echo urlencode($search); ?>&export=csv" class="btn-export">CSV Export</a>
            </form>
        </div>
        
        <table class="codes-table">
            <thead>
                <tr>
                    <th>Anlage</th>
                    <th>Code</th>
                    <th>Vorbehandlung</th>
                    <th>Hauptbehandlung</th>
                    <th>Passivierung</th>
                    <th>Nachbehandlung</th>
                    <th>Artikel</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($codes as $row): ?>
                <tr>
                    <td><?php echo htmlspecialchars($row['anlage'] === 'A6' ? 'A60' : $row['anlage']); ?></td>
                    <td class="code"><a href="details.php?code=<?php echo urlencode($row['code']); ?>" style="color: inherit; text-decoration: none;"><?php echo htmlspecialchars($row['code']); ?></a></td>
                    <td>
                        <span class="value"><?php echo htmlspecialchars($row['anlage'] === 'A6' ? 'A6' : $row['anlage']); ?>Vor<?php echo htmlspecialchars($row['vb']); ?></span>
                        <span class="text"><?php echo htmlspecialchars($row['vb_beschreibung'] ?: $row['vb_text']); ?></span>
                    </td>
                    <td>
                        <span class="value"><?php echo htmlspecialchars($row['anlage'] === 'A6' ? 'A6' : $row['anlage']); ?>Haupt<?php echo htmlspecialchars($row['hb']); ?></span>
                        <span class="text"><?php echo htmlspecialchars($row['hb_beschreibung'] ?: $row['hb_text']); ?></span>
                    </td>
                    <td>
                        <span class="value"><?php echo htmlspecialchars($row['anlage'] === 'A6' ? 'A6' : $row['anlage']); ?>Pass<?php echo htmlspecialchars($row['pas']); ?></span>
                        <span class="text"><?php echo htmlspecialchars($row['pas_beschreibung'] ?: $row['pas_text']); ?></span>
                    </td>
                    <td>
                        <span class="value"><?php echo htmlspecialchars($row['anlage'] === 'A6' ? 'A6' : $row['anlage']); ?>Nach<?php echo htmlspecialchars($row['nb']); ?></span>
                        <span class="text"><?php echo htmlspecialchars($row['nb_beschreibung'] ?: $row['nb_text']); ?></span>
                    </td>
                    <td class="count"><?php echo number_format($row['artikel_count'], 0, ',', '.'); ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        
        <?php if (empty($codes)): ?>
            <p class="no-results">Keine Codes gefunden.</p>
        <?php endif; ?>
    </div>
</body>
</html>