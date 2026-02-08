import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np

def extract_bungee_data():
    if not firebase_admin._apps:
        cred = credentials.Certificate('service_key.json')
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    doc_ref = db.collection('BungeeStrings').document('shared')
    doc = doc_ref.get()
    
    if not doc.exists:
        print("Error: No BungeeStrings document found.")
        return
    
    strings = doc.to_dict().get('strings', [])
    processed_strings = []
    
    for s in strings:
        string_id = s.get('stringId')
        calibration = s.get('calibrationData', [])
        strains, forces = [], []
        for p in calibration:
            if p.get('strain', 0) >= 0:
                strains.append(p.get('strain'))
                forces.append(p.get('force'))
        
        if len(strains) >= 4:
            coeffs = np.polyfit(strains, forces, 3)
            # Derivative coeffs for K_eff calculation in damping
            deriv = [3*coeffs[0], 2*coeffs[1], coeffs[2]]
            processed_strings.append({
                'id': string_id, 
                'coeffs': [round(float(c), 6) for c in coeffs],
                'deriv': [round(float(c), 6) for c in deriv]
            })

    ti_code = generate_ti_code(processed_strings)
    with open('BUNGEE.8xp.txt', 'w', encoding='utf-8') as f:
        f.write(ti_code)
    print("\nTI-Connect Compatible Model written to BUNGEE.8xp.txt")

def generate_ti_code(strings):
    code = []
    code.append("PROGRAM:BUNGEE")
    code.append(":ClrHome")
    code.append(":Disp \"SYNCHRONIZED MODEL\"")
    
    menu_items = [f"\"{s['id']}\",S{i+1}" for i, s in enumerate(strings[:6])]
    menu_items.append("\"MANUAL\",SM")
    code.append(f":Menu(\"SELECT STRING\",{','.join(menu_items)})")
    
    for i, s in enumerate(strings[:6]):
        code.append(f":Lbl S{i+1}")
        # Use standard list format {1,2,3} and standard store arrow ->
        combined = s['coeffs'] + s['deriv']
        code.append(f":{{{','.join(map(str, combined))}}}->L3")
        code.append(":Goto SP")
    
    code.append(":Lbl SM:Input \"LINEAR K:\",K:{{{0,0,K,0,0,0,K}}}->L3")
    
    code.append(":Lbl SP")
    code.append(":Input \"DROP HT(M):\",H")
    code.append(":Input \"MASS(G):\",M")
    code.append(":30->B:2->T:0.9->D")
    code.append(":H*100->H:M/1000->M")
    
    code.append(":Disp \"SOLVING (20S)...\"")
    code.append(":1->L:H-B-T->R")
    code.append(":For(I,1,15)")
    code.append(":(L+R)/2->C")
    code.append(":C->L1:Gosub SIM") # L1 used as L_SIM to be safe
    code.append(":If Y>T:Then:C->L:Else:C->R:End")
    code.append(":End")
    
    code.append(":ClrHome:Disp \"RECOMMENDED L:\",C")
    code.append(":Pause")
    code.append(":Stop")
    
    # Simulation Subroutine (Matches webpage logic)
    code.append(":Lbl SIM")
    code.append(":H-B->Y:0->V:0.01->dT")
    code.append(":-ln(D)/pi->Z")
    code.append(":M*9.8->F1:F1/L3(3)->S")
    code.append(":For(K,1,3):S-(L3(1)*S^3+L3(2)*S^2+L3(3)*S+L3(4)-F1)/(L3(5)*S^2+L3(6)*S+L3(7))->S:End")
    code.append(":(L3(5)*S^2+L3(6)*S+L3(7))/L1*100->K1") # KEFF = K1
    code.append(":2*Z*sqrt(M*K1)->B1") # BDAMP = B1
    
    code.append(":For(X1,0,4,dT)") # TS = X1
    code.append(":max(0,H-Y-B-L1)->X2:X2/L1->S1")
    code.append(":L3(1)*S1^3+L3(2)*S1^2+L3(3)*S1+L3(4)->F2")
    code.append(":(F2-M*9.8-B1*V/100)/M->A1")
    code.append(":V+A1*dT*100->V:Y+V*dT->Y")
    code.append(":If V>0 and X1>.2:Return:End")
    code.append(":End:Return")
    
    return "\n".join(code)

if __name__ == "__main__":
    extract_bungee_data()
