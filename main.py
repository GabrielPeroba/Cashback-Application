def calcular_cashback(valor_final_compra, is_vip = False):
    
    #Calculo do cashback base
    
    taxa_cashback_base = 0.05
    cashback_base = valor_final_compra * taxa_cashback_base
    
    #Promocao do Diretor Comercial
    
    if valor_final_compra > 500.00:
        
        cashback_base *= 2
        
    #Calculo do bonus VIP
        
    cashback_bonus_vip = 0.0
    if is_vip:
        
        taxa_bonus_vip = 0.10
        cashback_bonus_vip = cashback_base * taxa_bonus_vip
        
    #Cashback Final
        
    cashback_final = cashback_base + cashback_bonus_vip
    
    return round(cashback_final, 2)


if __name__ == "__main__":
    print("--- Sistema de Cashback ---\n")
    
    try:
        #Coletando os dados do usuário
        
        entrada_compra = input("Digite o valor original da compra (R$): ").replace(',', '.')
        valor_original = float(entrada_compra)
        
        #Coletando o desconto
        
        entrada_desconto = input("Digite a porcentagem de desconto (%): ").replace(',', '.')
        porcentagem_desconto = float(entrada_desconto)
        
        entrada_vip = input("O cliente é VIP? (S/N): ").strip().upper()
        is_vip = entrada_vip == 'S'
        
         #Tratamento de erro de percentagem
        
        if porcentagem_desconto < 0 or porcentagem_desconto > 100:
            
            print("\nErro: A porcentagem de desconto deve estar entre 0 e 100.")
            
        else:
            
            #Calculando o valor do desconto
            
            valor_desconto = valor_original * (porcentagem_desconto / 100)
            valor_final_compra = valor_original - valor_desconto
            
            #Calculando o cashback
            
            cashback = calcular_cashback(valor_final_compra, is_vip=is_vip)
            
            #Exibindo os resultados
            
            print("\n" + "="*30)
            print("       RESUMO DA COMPRA       ")
            print("="*30)
            print(f"Valor Original: R$ {valor_original:.2f}")
            print(f"Desconto ({porcentagem_desconto}%): R$ {valor_desconto:.2f}")
            print(f"Valor Final:    R$ {valor_final_compra:.2f}")
            print(f"Cliente VIP:    {'Sim' if is_vip else 'Não'}")
            print("-" * 30)
            print(f"CASHBACK:       R$ {cashback:.2f}")
            print("="*30 + "\n")
            
    except ValueError:
        
        print("\nErro: Por favor, insira números válidos para a compra e o desconto.")
